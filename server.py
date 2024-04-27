import http.server
import socketserver
import json
import urllib.parse
import books_utl
import socket

hostname = socket.gethostname()
# My ip address
ip_address = socket.gethostbyname(hostname)

hostName = ip_address
serverPort = 8000


class AppServer(http.server.SimpleHTTPRequestHandler):

    # check for get request
    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        url_query = dict(urllib.parse.parse_qsl(url.query))
        # return all products
        if url.path == '/categories':
            rows = books_utl.get_data('category', '', 'all')
            json_data = json.dumps(rows)
            books_utl.set_headers(self, 200, "application/json")
            # Send the JSON data as the response
            self.wfile.write(json_data.encode())
        elif url.path == '/books':
            # if the existence of a key in a dict
            cat_name = url_query['cat_name']
            cat_row = books_utl.get_data("category", "where cat_name ='" + cat_name + "'", 'one')
            all_books = books_utl.get_data('products', 'where category =' + str(cat_row[0]), 'all')

            json_data = json.dumps({'cat': cat_row, 'all_books': all_books})
            books_utl.set_headers(self, 200, "application/json")
            # Send the JSON data as the response
            self.wfile.write(json_data.encode())
        elif url.path == '/book':
            # if the existence of a key in a dict
            book_name = url_query['book_name']
            book_row = books_utl.get_data("products", "where book_name ='" + book_name + "'", 'one')
            cat_rows = books_utl.get_data('products', 'where category =' + str(book_row[7]), 'all')

            json_data = json.dumps({'book': book_row, 'all_books': cat_rows})
            books_utl.set_headers(self, 200, "application/json")
            # Send the JSON data as the response
            self.wfile.write(json_data.encode())
        else:
            get_file_data = books_utl.get_files(url)
            file_name = get_file_data['file_name']
            content_type = get_file_data['content_type']
            response_code = get_file_data['response_code']
            self.path = '/' + file_name
            file_to_open = open(file_name, "rb")
            books_utl.set_headers(self, response_code, content_type)
            self.wfile.write(file_to_open.read())
            file_to_open.close()

    def do_POST(self):
        url = urllib.parse.urlparse(self.path)
        response_data = []
        # return all products
        if url.path == '/add_new_book':
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            body_data = json.loads(body.decode('utf-8'))
            book_image_data = body_data['book_image']
            book_pdf_data = body_data['book_pdf']
            book_image_name = books_utl.base64_to_file(book_image_data, 'img/books/')
            book_pdf_name = books_utl.base64_to_file(book_pdf_data, 'pdf/')
            print(book_image_name, book_pdf_name)
            book_title = body_data['book_title']
            book_name = books_utl.title_to_slug(book_title)
            book_description = body_data['book_description']
            book_category = body_data['book_category']
            cat_row = books_utl.get_data("category", "where cat_name ='" + book_category + "'", 'one')
            column_values = '"' + book_name + '", ' + '"' + book_title + '", ' + '"' + book_description + '", ' + \
                            '"' + book_image_name + '", ' + '"' + book_pdf_name + '", ' + str(cat_row[0])

            row_id = books_utl.set_data('products', 'book_name, book_title, description, image , pdf, category',
                                        column_values)
            print(row_id)

            json_data = json.dumps('Saved')
            books_utl.set_headers(self, 200, "application/json")
            # Send the JSON data as the response
            self.wfile.write(json_data.encode())

        else:
            json_data = json.dumps({'Error'})
            books_utl.set_headers(self, 200, "application/json")
            # Send the JSON data as the response
            self.wfile.write(json_data.encode())


if __name__ == "__main__":
    with socketserver.TCPServer((hostName, serverPort), AppServer) as httpd:

        try:
            # #start server
            # nodemon  .\server.py
            # #OR
            # python .\server.py
            print("Server started http://%s:%s" % (hostName, serverPort))
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        httpd.server_close()
        print("Server stopped.")
