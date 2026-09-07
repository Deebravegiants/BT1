# [M] Gogs XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-px5r-fqj6-r2f8
CVE: CVE-2018-17031
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-px5r-fqj6-r2f8
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.12.0

## Details
In Gogs 0.11.53, an attacker can use a crafted .eml file to trigger MIME type sniffing, which leads to XSS, as demonstrated by Internet Explorer, because an "X-Content-Type-Options: nosniff" header is not sent.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-17031
- https://github.com/gogs/gogs/issues/5397
- https://github.com/gogs/gogs/pull/6008
- https://github.com/gogs/gogs/commit/e14b6abf9dae13bc087c9d9db8fe7c7a5125c792
- https://github.com/gogs/gogs
