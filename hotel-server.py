from http.server import HTTPServer, BaseHTTPRequestHandler


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/callTaxi":
            print("-------------------------------------------")
            print("### CALL TAXI")
            full_name = self.headers.get("full_name")
            departure_place = self.headers.get("departure_place")
            departure_date = self.headers.get("departure_date")
            destination_place = self.headers.get("destination_place")

            print(f"Full name: \t\t {full_name}")
            print(f"Departure place: \t\t {departure_place}")
            print(f"Departure date: \t\t {departure_date}")
            print(f"Destination place: \t\t {destination_place}")
            print("-------------------------------------------")

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response_content = b'{"message": "Taxi is on its way!"}'
            self.wfile.write(response_content)
        elif self.path == "/checkIn":
            print("-------------------------------------------")
            print("### CHECK IN")
            first_name = self.headers.get("first_name")
            last_name = self.headers.get("last_name")
            checkin_date = self.headers.get("checkin_date")

            print(f"First name: \t\t {first_name}")
            print(f"Last name: \t\t {last_name}")
            print(f"Checkin date: \t\t {checkin_date}")
            print("-------------------------------------------")

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response_content = b'{"message": "Check-in was successful!"}'
            self.wfile.write(response_content)
        elif self.path == "/checkOut":
            print("-------------------------------------------")
            print("### CHECK OUT")
            first_name = self.headers.get("first_name")
            last_name = self.headers.get("first_name")
            checkout_date = self.headers.get("checkout_date")

            print(f"First name: \t\t {first_name}")
            print(f"Last name: \t\t {last_name}")
            print(f"Checkout date: \t\t {checkout_date}")
            print("-------------------------------------------")

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response_content = b'{"message": "Check-out was successful!"}'
            self.wfile.write(response_content)
        else:
            print("False response!")


# Set up the HTTP server
def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler):
    server_address = ('', 8081)  # Listen on port 8081
    httpd = server_class(server_address, handler_class)
    print("Start hotel server...")
    httpd.serve_forever()


# Run the server
if __name__ == "__main__":
    run()
