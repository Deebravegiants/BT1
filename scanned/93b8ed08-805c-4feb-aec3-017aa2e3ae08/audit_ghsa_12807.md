# [H] Parse Server option `masterKeyIps` vulnerability to IP spoofing

## Summary
Severity: High
Advisory: GHSA-vm5r-c87r-pf6x
CVE: CVE-2023-22474
CWE: CWE-290
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2023-01-31
Source: https://github.com/advisories/GHSA-vm5r-c87r-pf6x
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=0 <5.4.1

## Details
### Impact

Parse Server uses the request header `x-forwarded-for` to determine the client IP address. If Parse Server doesn't run behind a proxy server, then a client can set this header and Parse Server will trust the value of the header. The incorrect client IP address will be used by various features in Parse Server. This allows to circumvent the security mechanism of the Parse Server option `masterKeyIps` by setting an allowed IP address as the `x-forwarded-for` header value.

### Patches

The mechanism to determine the client IP address has been rewritten. The correct IP address determination now requires to set the Parse Server option `trustProxy` accordingly, see the express framework's [trust proxy](https://expressjs.com/en/guide/behind-proxies.html) setting.

### References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-vm5r-c87r-pf6x
- https://expressjs.com/en/guide/behind-proxies.html

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-vm5r-c87r-pf6x
- https://nvd.nist.gov/vuln/detail/CVE-2023-22474
- https://github.com/parse-community/parse-server/commit/e016d813e083ce6828f9abce245d15b681a224d8
- https://github.com/parse-community/parse-server
