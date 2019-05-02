from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import unquote, parse_qs
import re
import html
from db_setup import Restaurant
import db_api

restaurants_list_html = '''
                <!doctype html>
                <html>
                    <head>
                        <title>Restaurants</title>
                    </head>
                    <body>
                        <a href="/restaurants/new">Add New Restaurant</a>
                        <ol>
                        {bodycontent}
                        </ol>
                    <body>
                </html>
'''

new_restaurant_html = '''
                <!doctype html>
                <html>
                    <head>
                        <title>Restaurants</title>
                    </head>
                    <body>
                        <h2>Add new restaurant</h2>
                        <form method="post" action="/restaurants/new">
                            <input name="rest-name" type="text" />
                            <input type="submit" value="Add" />
                        </form>
                    <body>
                </html>
'''

edit_restaurant_html = '''
                <!doctype html>
                <html>
                    <head>
                        <title>Restaurants</title>
                    </head>
                    <body>
                        <h2>Rename Restaurant</h2>
                        <form method="post" action="/restaurants/{id}/edit">
                            <input name="rest-name" type="text" value="{currentname}" />
                            <input type="submit" value="Rename" />
                        </form>
                    <body>
                </html>
'''

delete_restaurant_html = '''
                <!doctype html>
                <html>
                    <head>
                        <title>Restaurants</title>
                    </head>
                    <body>
                        <h2>Delete Restaurant - {name}?</h2>
                        <form method="post" action="/restaurants/{id}/delete">
                            <input type="submit" value="Delete" />
                        </form>
                    <body>
                </html>
'''



class webserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                restaurants = db_api.getRestaurants()
                output = ''
                for restaurant in restaurants:
                    output += '''
                        <li>{name}
                            <a href="/restaurants/{id}/edit">Edit</a>
                            <a href="/restaurants/{id}/delete">Delete</a>
                        </li>
                        '''.format(id=restaurant.id, name=restaurant.name)
                output = restaurants_list_html.format(bodycontent=output)
                self.wfile.write(output.encode())
                return

            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(new_restaurant_html.encode())
                return

            if re.search(r'^/restaurants/[\d]*/edit$', self.path):
                match = re.search(r'[\d]+', self.path)
                id = self.path[match.span()[0]:match.span()[1]]
                restaurant = db_api.getRestaurant(id)
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = edit_restaurant_html.format(id=restaurant.id, currentname=html.escape(restaurant.name))
                self.wfile.write(output.encode())
                return

            if re.search(r'^/restaurants/[\d]*/delete$', self.path):
                match = re.search(r'[\d]+', self.path)
                id = self.path[match.span()[0]:match.span()[1]]
                restaurant = db_api.getRestaurant(id)
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = delete_restaurant_html.format(id=restaurant.id, name=html.escape(restaurant.name))
                self.wfile.write(output.encode())
                return

        except IOError:
            self.send_error(404, "File Not Found %s" % self.path)

    def do_POST(self):
        if self.path.endswith("/restaurants/new"):
            length = int(self.headers.get('Content-length', 0))
            body = self.rfile.read(length).decode()
            params = parse_qs(body)

            self.send_response(301)

            restaurantName = params['rest-name'][0]
            db_api.addRestaurant(restaurantName)

            self.send_response(301)
            self.send_header('Location', "/restaurants")
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            # output = new_restaurant_html.format(add_confirm_message='Restaurant added!')
            # self.wfile.write(output.encode())
            # print(output)
            return

        if re.search(r'^/restaurants/[\d]*/edit$', self.path):
            length = int(self.headers.get('Content-length', 0))
            body = self.rfile.read(length).decode()
            params = parse_qs(body)

            match = re.search(r'[\d]+', self.path)
            id = self.path[match.span()[0]:match.span()[1]]
            restaurant = db_api.getRestaurant(id)
            restaurant.name = params['rest-name'][0]
            db_api.updateRestaurant(restaurant)

            self.send_response(301)
            self.send_header('Location', "/restaurants")
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            return

        if re.search(r'^/restaurants/[\d]*/delete$', self.path):
            length = int(self.headers.get('Content-length', 0))
            body = self.rfile.read(length).decode()
            params = parse_qs(body)

            match = re.search(r'[\d]+', self.path)
            id = self.path[match.span()[0]:match.span()[1]]
            restaurant = db_api.getRestaurant(id)
            db_api.delete(restaurant)

            self.send_response(301)
            self.send_header('Location', "/restaurants")
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            return
        

def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webserverHandler)
        print("Web server running on port %s" % port)
        server.serve_forever()
    except KeyboardInterrupt:
        print("^C entered, stopping web server...")
        server.socket.close()

if __name__ == '__main__':
    main()
