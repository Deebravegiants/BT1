# [M] MCP Ruby SDK: Unbounded line buffer in stdio transports leads to memory exhaustion (DoS)

## Summary
Severity: Medium
Advisory: GHSA-7683-3w9x-ch42
CVE: CVE-2026-63119
CWE: CWE-400, CWE-770
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-30
Source: https://github.com/advisories/GHSA-7683-3w9x-ch42
Type: github-advisory

## Affected
- RubyGems: `mcp` — affected >=0 <0.23.0

## Details
## Summary

The stdio transports in `MCP::Server::Transports::StdioTransport` and `MCP::Client::Stdio` read newline-delimited JSON-RPC frames using `IO#gets` with no `limit` argument. CRuby's `IO#gets` with no limit reads from the current position until the next separator (`\n`) with no upper bound on the returned string length. A peer that streams bytes without ever emitting a newline causes `gets` to accumulate the entire stream in a single Ruby `String` until the process is killed by the operating-system OOM killer.

This is the same vulnerability class tracked in sibling MCP SDKs as GHSA-74gp-qhv5-v493 (Kotlin), GHSA-wqgc-pwpr-pq7r (TypeScript), GHSA-655q-2283-6jgj (Python), and others. It was identified during a cross-SDK audit; ruby-sdk had no prior report.

## Affected code

Verified at `main` @ `cf44475c`.

### Server transport — [`lib/mcp/server/transports/stdio_transport.rb`](https://github.com/modelcontextprotocol/ruby-sdk/blob/cf44475c/lib/mcp/server/transports/stdio_transport.rb)

```ruby
# line 23
while @open && (line = $stdin.gets)        # <-- no limit argument
  response = @session.handle_json(line.strip)
  ...

# line 76
while @open && (line = $stdin.gets)        # <-- no limit argument
  begin
    parsed = JSON.parse(line.strip, symbolize_names: true)
```

`$stdin` is the raw process global (only `set_encoding` is applied at line 16); there is no wrapper imposing a length limit.

### Client transport — [`lib/mcp/client/stdio.rb`](https://github.com/modelcontextprotocol/ruby-sdk/blob/cf44475c/lib/mcp/client/stdio.rb)

```ruby
# line 150
@stdin, @stdout, @stderr, @wait_thread = Open3.popen3(spawn_env, @command, *@args)

# line 228
line = @stdout.gets                         # <-- no limit argument
raise_connection_error!(method, params) if line.nil?
parsed = JSON.parse(line.strip)
```

`@stdout` is the raw `IO` returned by `Open3.popen3`. The `@read_timeout` guard at line 227 (`wait_for_readable!`) only gates the `IO.select` before `gets` is invoked; once bytes are flowing, `gets` blocks indefinitely accumulating into one string.

## Impact

Denial of service via memory exhaustion. A peer that controls the byte stream delivered to the stdio transport can grow a single Ruby `String` until the process exhausts available memory.

**Threat-model caveat (important):** In the default stdio deployment, the peer process already holds local execution privileges equal to or greater than the victim:
- On the **server** side (`StdioTransport#open`), the writer to `$stdin` is the parent process that spawned the server, which already holds `Process.kill`, environment control, and filesystem access over the child. This direction is a robustness defect rather than a security boundary in typical deployments.
- On the **client** side (`Client::Stdio#read_response`), the writer is the third-party MCP server binary the host application chose to spawn via `Open3.popen3`. In an unsandboxed deployment that binary already has local code execution as the host user.

This issue is primarily a security concern for:
- (a) host applications that **sandbox** the spawned MCP server (container, restricted user, seccomp) while piping its stdout to an unsandboxed host process — an unbounded `gets` lets a memory-capped sandboxed process exhaust the unconstrained host;
- (b) **HTTP-to-stdio bridge** deployments that forward bytes from a remote peer to a stdio server's stdin (note: surveyed bridges re-frame JSON-RPC and emit their own newlines, mitigating this in practice);
- (c) **robustness** against non-malicious servers that emit large unterminated output (misconfigured logging to stdout, runaway loops), which can crash the host process and all other MCP sessions it manages.

The bug fires before the JSON-RPC `initialize` handshake, since `gets` cannot return until `\n` arrives.

## Reproduction

```ruby
# poc_ruby_stdio_oom.rb — drives the real client transport against a producer that never emits \n
require "mcp/client/stdio"

# `yes` writes "y\n" — instead use a producer that never sends \n:
producer = %q{ruby -e 'STDOUT.sync=true; loop { print "A" * 65536 }'}

client = MCP::Client::Stdio.new(command: "bash", args: ["-c", producer])
client.start
# any request triggers read_response → @stdout.gets → unbounded String growth
client.send_request(method: "initialize", params: {})
```

Observed: process RSS grows linearly with bytes produced; `gets` never returns; process is OOM-killed.

## Suggested fix

`IO#gets` accepts a second `limit` argument. Apply a configurable maximum line length (default suggested: 4 MiB — large enough for any realistic JSON-RPC frame including base64-embedded images) at all three call sites, and treat an over-limit line as a transport error that closes the connection:

```ruby
MAX_LINE_BYTES = 4 * 1024 * 1024

while @open && (line = $stdin.gets("\n", MAX_LINE_BYTES))
  unless line.end_with?("\n")
    # gets returned because the limit was hit, not because a newline arrived
    raise MCP::TransportError, "stdio frame exceeds #{MAX_LINE_BYTES} bytes without newline"
  end
  ...
end
```

Apply the same pattern at `stdio_transport.rb:76` and `client/stdio.rb:228`. Expose `MAX_LINE_BYTES` as a constructor option on both transports for callers with legitimate large-frame needs.

## Credit

Identified during a cross-SDK audit of the stdio unbounded-buffer vulnerability class, prompted by GHSA-74gp-qhv5-v493 (reporter: tonghuaroot).

## References
- https://github.com/modelcontextprotocol/ruby-sdk/security/advisories/GHSA-7683-3w9x-ch42
- https://nvd.nist.gov/vuln/detail/CVE-2026-63119
- https://github.com/modelcontextprotocol/ruby-sdk/commit/267b8fa6285453525c81ce43db6b7dcd7a8a8c2f
- https://github.com/modelcontextprotocol/ruby-sdk
- https://github.com/modelcontextprotocol/ruby-sdk/releases/tag/v0.23.0
