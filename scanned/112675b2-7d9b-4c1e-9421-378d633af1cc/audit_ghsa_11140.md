# [M] Undici has CRLF Injection in undici via `upgrade` option

## Summary
Severity: Medium
Advisory: GHSA-4992-7rv2-5pvq
CVE: CVE-2026-1527
CWE: CWE-93
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-4992-7rv2-5pvq
Type: github-advisory

## Affected
- npm: `undici` — affected >=0 <6.24.0
- npm: `undici` — affected >=7.0.0 <7.24.0

## Details
### Impact

When an application passes user-controlled input to the `upgrade` option of `client.request()`, an attacker can inject CRLF sequences (`\r\n`) to:

1. Inject arbitrary HTTP headers
2. Terminate the HTTP request prematurely and smuggle raw data to non-HTTP services (Redis, Memcached, Elasticsearch)

The vulnerability exists because undici writes the `upgrade` value directly to the socket without validating for invalid header characters:

```javascript
// lib/dispatcher/client-h1.js:1121
if (upgrade) {
  header += `connection: upgrade\r\nupgrade: ${upgrade}\r\n`
}
```

### Patches

 Patched in the undici version v7.24.0 and v6.24.0. Users should upgrade to this version or later.

### Workarounds

Sanitize the `upgrade` option string before passing to undici:

```javascript
function sanitizeUpgrade(value) {
  if (/[\r\n]/.test(value)) {
    throw new Error('Invalid upgrade value')
  }
  return value
}

client.request({
  upgrade: sanitizeUpgrade(userInput)
})
```

## References
- https://github.com/nodejs/undici/security/advisories/GHSA-4992-7rv2-5pvq
- https://nvd.nist.gov/vuln/detail/CVE-2026-1527
- https://hackerone.com/reports/3487198
- https://cna.openjsf.org/security-advisories.html
- https://github.com/nodejs/undici
