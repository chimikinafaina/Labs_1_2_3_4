import datetime
import ftplib
import markdown


def save_pokemon_info(name):
    USERNAME = ''
    PASSWORD = ''
    PORT = 21
    ftp = ftplib.FTP('', USERNAME, PASSWORD)
    files = ftp.nlst()
    print(files)
    markdown_text = f"# {name}\n"
    html_text = markdown.markdown(markdown_text)
    file_name = f"{name}.md"
    current_date = datetime.datetime.now().strftime('%d.%m.%Y')
    file_path = f"{current_date}/{file_name}"
    if current_date in ftp.nlst():
        ftp.cwd(current_date)
    else:
        ftp.mkd(current_date)
        ftp.cwd(current_date)

    with open(current_date, 'wb') as f:
        f.write(markdown_text.encode())
    ftp.storbinary('STOR ' + file_name, open(current_date, 'rb'))
    ftp.quit()


if __name__ == '__main__':
    save_pokemon_info('cool')
    save_pokemon_info('ex')