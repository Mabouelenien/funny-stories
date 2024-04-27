import sqlite3
import base64
import time

def get_files(url):
    response_code = 200
    content_type = 'text/html'
    file_name = url.path[1:]
    file_split_list = file_name.split('.')
    file_ext = file_split_list[len(file_split_list) - 1]
    file_ext = file_ext.lower()
    allowed_ext = ['html', 'css', 'png', 'webp', 'ico', 'jpg', 'jpeg', 'pdf']
    if file_ext in allowed_ext:
        if file_ext == 'css':
            content_type = 'text/css'
        elif file_ext == 'png':
            content_type = 'image/png'
        elif file_ext == 'webp':
            content_type = 'image/webp'
        elif file_ext == 'ico':
            content_type = 'image/vnd.microsoft.icon'
        elif file_ext == 'jpg' or file_ext == 'jpeg':
            content_type = 'image/jpeg'
        elif file_ext == 'pdf':
            content_type = 'application/pdf'
        else:
            content_type = 'text/html'
    else:
        if url.path == '/':
            file_name = 'index.html'
            response_code = 200
        else:
            file_name = '404.html'
            response_code = 404
    return {'file_name': file_name, 'content_type': content_type, 'response_code': response_code}


def get_data(table, sub_sql='', fetch_one_or_all='one'):
    # connection object
    connection = sqlite3.connect('database/books.db')
    # cursor object
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM " + table + " " + sub_sql)

    if fetch_one_or_all == 'one':
        # get one row
        result = cursor.fetchone()
    else:
        # get all rows
        result = cursor.fetchall()

    # Close the connection
    connection.close()
    return result


def set_data(table, columns, columns_values):
    # connection object
    #connection = sqlite3.connect('database/books.db')
    # sqlite3.connect to remote host
    connection = sqlite3.connect('http://mabouelenien.pythonanywhere.com/static/books.db')
    # cursor object
    cursor = connection.cursor()
    cursor.execute("INSERT INTO " + table + "(" + columns + ") " + "values(" + columns_values + ") ")
    connection.commit()
    last_row_id = cursor.lastrowid
    cursor.close()
    return last_row_id


def title_to_slug(title):
    special_characters = ['@', '#', '$', '*', '&', "'", '"', '_', ',']
    for i in special_characters:
        # Replace the special character with an empty string
        title = title.replace(i, " ")

    slug = title.replace(" ", "-").lower()
    return slug


def base64_to_file(base64_string, output_path):
    data_image = base64_string.split(',', 1)

    ext = data_image[0]  # data:image/jpeg;
    ext = ext.split('/')[1]
    ext = ext.split(';')[0]
    output_filename = "book_" + str(int(time.time())) + '.' + ext

    # Decode Base64 data to bytes
    image_data = base64.b64decode(data_image[1])
    fh = open(output_path + output_filename, "wb")
    fh.write(image_data)
    fh.close()
    return output_filename


def set_headers(self, response_code, content_type):
    self.send_response(response_code)
    self.send_header('Access-Control-Allow-Origin', '*')
    self.send_header("Content-type", content_type)
    self.end_headers()


def get_field_value(data, field):
    field_start = data.find(field) + len(field) + 4  # Find the start of the field value
    field_end = data.find(b'------', field_start)  # Find the end of the field value
    return data[field_start:field_end].decode('utf-8')
