import random
import asyncio

# Зчитуємо файл blacklist.txt і готуємо список заблокованих доменів
BLOCKED = [line.strip().lower().encode() for line in open('blacklist.txt', 'r', encoding='utf-8') if line.strip()]
TASKS = []


async def main(host, port):
    server = await asyncio.start_server(new_conn, host, port)
    print(f"Proxy server is running on {host}:{port}")
    await server.serve_forever()


async def pipe(reader, writer):
    while not reader.at_eof() and not writer.is_closing():
        try:
            writer.write(await reader.read(1500))
            await writer.drain()
        except Exception as e:
            print(f"Pipe error: {e}")
            break
    writer.close()


async def new_conn(local_reader, local_writer):
    try:
        http_data = await local_reader.read(1500)
        request_line = http_data.split(b"\r\n")[0]
        method, target, _ = request_line.split(b" ")

        # Перевірка, чи це CONNECT-запит
        if method != b"CONNECT":
            local_writer.close()
            return

        host, port = target.split(b":")

        # Перевіряємо, чи хост заблокований
        if any(blocked in host.lower() for blocked in BLOCKED):
            print(f"Blocked: {host.decode()}")
            local_writer.close()
            return

        # Відповідаємо клієнту, що з'єднання встановлено
        local_writer.write(b'HTTP/1.1 200 OK\r\n\r\n')
        await local_writer.drain()

        # Встановлюємо з'єднання з віддаленим сервером
        remote_reader, remote_writer = await asyncio.open_connection(host.decode(), int(port))

        # Додаємо завдання для пересилання даних
        TASKS.append(asyncio.create_task(pipe(local_reader, remote_writer)))
        TASKS.append(asyncio.create_task(pipe(remote_reader, local_writer)))

    except Exception as e:
        print(f"Error in new_conn: {e}")
        local_writer.close()


if __name__ == '__main__':
    try:
        asyncio.run(main(host='127.0.0.1', port=8881))
    except KeyboardInterrupt:
        print("Server stopped")
