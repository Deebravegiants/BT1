# [M] client-certificate-auth Vulnerable to Open Redirect via Host Header Injection in HTTP-to-HTTPS redirect

## Summary
Severity: Medium
Advisory: GHSA-m4w9-gch5-c2g4
CVE: CVE-2026-25651
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-02-06
Source: https://github.com/advisories/GHSA-m4w9-gch5-c2g4
Type: github-advisory

## Affected
- npm: `client-certificate-auth` — affected >=0.2.1 <1.0.0

## Details
### Summary

Versions 0.2.1 and 0.3.0 of `client-certificate-auth` contain an open redirect vulnerability. The middleware unconditionally redirects HTTP requests to HTTPS using the unvalidated `Host` header, allowing an attacker to redirect users to arbitrary domains.

### Vulnerable Code

```javascript
// lib/clientCertificateAuth.js (versions 0.2.1, 0.3.0)
if (!req.secure && req.header('x-forwarded-proto') != 'https') {
  return res.redirect('https://' + req.header('host') + req.url);
}
```

### Attack Scenario

1. Attacker crafts a link: `http://vulnerable-app.example.com/login`
2. When victim clicks, attacker intercepts and injects header: `Host: attacker.com`
3. Server responds: `302 Found → https://attacker.com/login`
4. Victim is redirected to attacker-controlled site

### Impact

- **Phishing**: Attackers can use trusted domain links to redirect victims to credential-harvesting pages
- **OAuth/SSO Token Theft**: In authentication flows, authorization codes or tokens may leak via redirect
- **Referer Leakage**: Sensitive URL parameters may be exposed to attacker domains via the Referer header
- **Cache Poisoning**: In deployments with shared caches, malicious redirects may be cached and served to other users

### Exploitability

Exploitation requires that HTTP traffic reaches the Node.js application without TLS termination setting `x-forwarded-proto: https`. This condition is uncommon in production deployments behind modern reverse proxies or load balancers, which limits real-world exploitability.

### Fix

The vulnerable redirect behavior has been completely removed in version 1.0.0.

```bash
npm install client-certificate-auth@^1.0.0
```

### Workarounds

If upgrading is not immediately possible:

1. Block HTTP traffic at the network/load balancer level
2. Ensure your reverse proxy always sets `x-forwarded-proto: https`
3. Add middleware before `clientCertificateAuth` to validate the `Host` header against an allowlist

### References

- [CWE-601: URL Redirection to Untrusted Site](https://cwe.mitre.org/data/definitions/601.html)
- [OWASP: Unvalidated Redirects and Forwards](https://cheatsheetseries.owasp.org/cheatsheets/Unvalidated_Redirects_and_Forwards_Cheat_Sheet.html)
- [Fix Commit](https://github.com/tgies/client-certificate-auth/commit/8fc995e953db483495be46862965e50fe9e1cc52)

## References
- https://github.com/tgies/client-certificate-auth/security/advisories/GHSA-m4w9-gch5-c2g4
- https://nvd.nist.gov/vuln/detail/CVE-2026-25651
- https://github.com/tgies/client-certificate-auth/commit/8fc995e953db483495be46862965e50fe9e1cc52
- https://github.com/tgies/client-certificate-auth
- https://github.com/tgies/client-certificate-auth/releases/tag/v1.0.0
