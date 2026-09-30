# [H] body-parser vulnerable to denial of service when url encoding is enabled

## Summary
Severity: High
Advisory: GHSA-qwcr-r2fm-qrc7
CVE: CVE-2024-45590
CWE: CWE-405
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-09-10
Source: https://github.com/advisories/GHSA-qwcr-r2fm-qrc7
Type: github-advisory

## Affected
- npm: `body-parser` — affected >=0 <1.20.3

## Details
### Impact

body-parser <1.20.3 is vulnerable to denial of service when url encoding is enabled. A malicious actor using a specially crafted payload could flood the server with a large number of requests, resulting in denial of service.

### Patches

this issue is patched in 1.20.3

### References

## References
- https://github.com/expressjs/body-parser/security/advisories/GHSA-qwcr-r2fm-qrc7
- https://nvd.nist.gov/vuln/detail/CVE-2024-45590
- https://github.com/expressjs/body-parser/commit/b2695c4450f06ba3b0ccf48d872a229bb41c9bce
- https://github.com/expressjs/body-parser
