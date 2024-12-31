import unittest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from nodpi import new_conn, BLOCKED


class TestProxyServer(unittest.TestCase):
    def setUp(self):
        # Ініціалізуємо чорний список для тестування
        self.blocked_domains = [b"youtube.com", b"google.com"]

    def test_blocked_domains(self):
        # Тестуємо, чи домени з чорного списку блокуються
        for domain in self.blocked_domains:
            with self.subTest(domain=domain):
                self.assertTrue(any(blocked in domain.lower() for blocked in BLOCKED))

    @patch("main.pipe")
    @patch("asyncio.open_connection")
    async def test_allowed_connection(self, mock_open_connection, mock_pipe):
        # Імітуємо з'єднання для дозволених доменів
        mock_open_connection.return_value = (AsyncMock(), AsyncMock())
        mock_pipe.side_effect = AsyncMock()

        local_reader = AsyncMock()
        local_writer = MagicMock()

        # Вхідний запит для дозволеного домену
        http_data = b"CONNECT allowed.com:443 HTTP/1.1\r\n\r\n"
        local_reader.read.return_value = http_data

        await new_conn(local_reader, local_writer)

        # Перевіряємо, чи викликали встановлення з'єднання з віддаленим сервером
        mock_open_connection.assert_called_with("allowed.com", 443)

        # Перевіряємо, чи відправлено відповідь клієнту
        local_writer.write.assert_called_with(b'HTTP/1.1 200 OK\r\n\r\n')

    async def test_blocked_connection(self):
        # Імітуємо з'єднання для заблокованого домену
        local_reader = AsyncMock()
        local_writer = MagicMock()

        # Вхідний запит для заблокованого домену
        http_data = b"CONNECT youtube.com:443 HTTP/1.1\r\n\r\n"
        local_reader.read.return_value = http_data

        await new_conn(local_reader, local_writer)

        # Перевіряємо, чи було закрито з'єднання
        local_writer.close.assert_called()

    async def test_invalid_method(self):
        # Тестуємо випадок, коли запит не є CONNECT
        local_reader = AsyncMock()
        local_writer = MagicMock()

        # Вхідний запит із некоректним методом
        http_data = b"GET / HTTP/1.1\r\n\r\n"
        local_reader.read.return_value = http_data

        await new_conn(local_reader, local_writer)

        # Перевіряємо, чи було закрито з'єднання
        local_writer.close.assert_called()

    async def test_empty_request(self):
        # Тестуємо випадок, коли запит порожній
        local_reader = AsyncMock()
        local_writer = MagicMock()

        # Порожній запит
        local_reader.read.return_value = b""

        await new_conn(local_reader, local_writer)

        # Перевіряємо, чи було закрито з'єднання
        local_writer.close.assert_called()


if __name__ == "__main__":
    unittest.main()
