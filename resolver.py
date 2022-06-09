from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import requests
import json
from urllib import parse
import copy


class CustomHandler(BaseHTTPRequestHandler):

    blockservice = "https://blockservice.nebulamden.finance"

    def resolve(self, name):
        if(len(name) == 64):
            return '{"status": "success", "response" : "'+name+'"}'
        if(name.startswith("con_")):
            return '{"status": "success", "response" : "'+name+'"}'
        if(" " in name):
            return '{"status": "error", "response" : "Spaces in Names are not allowed"}'  
        

        if name.endswith(".tau"):
            name = name.replace(".tau", "")
            name_to_address = {}

            url = requests.get(self.blockservice + '/current/all/con_nameservice_v3', headers={'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36'}, timeout=10)
            contract_data = json.loads(url.text)
            balances = contract_data["con_nameservice_v3"]["collection_balances"]
            copy_balances = copy.deepcopy(balances)
            for address in copy_balances:
                for nft in copy_balances[address]:
                    if copy_balances[address][nft] == 0:
                        balances[address].pop(nft)
                        
                
            for address in balances:
                name_to_address[address] = []
            for key in name_to_address:
                name_to_address[key] = balances[key]
            name_to_address = {k: oldk for oldk, oldv in name_to_address.items() for k in oldv}
            try:
                return '{"status": "success", "response" : "'+name_to_address[name]+'"}'
            except KeyError:
                return '{"status": "error", "response" : "Name does not exist"}'
        else:
            return '{"status": "error", "response" : "To use the Name Service, you have to add .tau"}'

    def buildResponse(self, data):
        url_path = data.path.split("/")[1]
        response = ""
        if "resolve" in url_path:
            response = self.resolve(data.path.split("/")[2])
            print("Response: " + str(response))
            self.wfile.write(response.encode('utf-8'))

    def setHeaders(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def do_GET(self):
        params = parse.urlsplit(self.path)
        self.setHeaders()
        self.buildResponse(params)


class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass

def run():
    server = ThreadingSimpleServer(('0.0.0.0', 2000), CustomHandler)
    server.serve_forever()


if __name__ == '__main__':
    run()
