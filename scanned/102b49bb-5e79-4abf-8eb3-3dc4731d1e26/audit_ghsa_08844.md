# [M] OpenClaude MCP OAuth Callback: State Check Bypass via error Param Leads to DoS

## Summary
Severity: Medium
Advisory: GHSA-c73c-x77g-854r
CVE: CVE-2026-42073
CWE: CWE-352, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-c73c-x77g-854r
Type: github-advisory

## Affected
- npm: `@gitlawb/openclaude` — affected >=0 <0.5.1

## Details
# OAuth State Validation Bypass via `error` Parameter Causes Local Server DoS in MCP Auth Callback
---

## Description

The OpenClaude MCP authentication flow starts a temporary local HTTP server to handle OAuth callbacks. To prevent CSRF attacks, the server validates a `state` parameter against an internally stored value. However, due to a logic flaw in the order of conditionals, an attacker can completely bypass this check and force the server to shut down — without knowing the `state` value at all.

The vulnerable code looks like this:

```typescript
if (!error && state !== oauthState) {
    rejectOnce(new Error('OAuth state mismatch - possible CSRF attack'))
    return
}

if (error) {
    cleanup()
    rejectOnce(new Error(errorMessage))
    return
}
```

When a request arrives with an `error` query parameter (e.g., `?error=anything`), the first condition becomes `false` because `!error` evaluates to `false`. This means the CSRF check is **never reached**. Execution falls through to the second block, where `cleanup()` is called — shutting down the local server and terminating the user's active authentication session.

The attacker does not need to know the `state` value. Any request containing an `error` parameter is enough to trigger the shutdown.

---

## Impact

- The user's OAuth flow is silently terminated mid-session
- The local callback server is shut down (Denial of Service)
- Can be triggered remotely via a malicious web page using a cross-origin request (CSRF)
- No authentication or prior knowledge of the `state` value is required

---

## Steps to Reproduce

Save the following as `poc.js` and run with Node.js:

```javascript
import { createServer } from 'http';
import { parse } from 'url';

const expectedState = "secure_state_abc123";

const server = createServer((req, res) => {
    const parsedUrl = parse(req.url || '', true);
    const { pathname, query } = parsedUrl;
    const { state, error } = query;

    if (pathname === '/callback') {

        // Vulnerable: error param causes state check to be skipped entirely
        if (!error && state !== expectedState) {
            res.writeHead(400);
            res.end('State mismatch');
            console.log('[-] CSRF attempt blocked.');
            return;
        }

        if (error) {
            res.writeHead(200);
            res.end(`Error: ${error}`);
            console.log(`[!] Server shutting down. Triggered by: ${error}`);
            server.close();
            return;
        }
    }
});

server.listen(12345, '127.0.0.1', () => {
    console.log('Listening on http://127.0.0.1:12345');
});
```

**Terminal 1 — start the server:**
```bash
node poc.js
```

**Terminal 2 — trigger the bypass:**
```bash
curl "http://127.0.0.1:12345/callback?error=triggered"
```

**Expected result:** Server shuts down immediately. The `state` value was never checked.

---

## Root Cause

The CSRF protection is conditioned on `!error`, meaning it is silently disabled whenever an `error` parameter is present. The two checks need to be decoupled — state validation must happen first, independently of any other parameters.

---

## Fix

Move the `state` check before the `error` check, and remove the dependency on `!error`:

```typescript
// Fixed
if (state !== oauthState) {
    cleanup()
    rejectOnce(new Error('OAuth state mismatch - possible CSRF attack'))
    return
}

if (error) {
    cleanup()
    rejectOnce(new Error(errorMessage))
    return
}
```

With this change, any request — whether it contains an `error` parameter or not — must first pass the state validation before any further processing occurs.

---

Credit: Xanlar Agamalizade

## References
- https://github.com/Gitlawb/openclaude/security/advisories/GHSA-c73c-x77g-854r
- https://nvd.nist.gov/vuln/detail/CVE-2026-42073
- https://github.com/Gitlawb/openclaude/commit/739b8d1f40fde0e401a5cbd2b9a55d88bd5124ad
- https://github.com/Gitlawb/openclaude
- https://github.com/Gitlawb/openclaude/releases/tag/v0.5.1
