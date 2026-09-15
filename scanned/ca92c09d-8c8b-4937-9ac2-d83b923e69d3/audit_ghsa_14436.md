# [H] Appwrite Server-Side Request Forgery vulnerability

## Summary
Severity: High
Advisory: GHSA-hxgx-584x-vwm8
CVE: CVE-2023-27159
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-03-31
Source: https://github.com/advisories/GHSA-hxgx-584x-vwm8
Type: github-advisory

## Affected
- Packagist: `appwrite/server-ce` — affected >=0

## Details
Appwrite up to v1.2.1 was discovered to contain a Server-Side Request Forgery (SSRF) via the component `/v1/avatars/favicon`. This vulnerability allows attackers to access network resources and sensitive information via a crafted GET request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-27159
- https://gist.github.com/b33t1e/43b26c31e895baf7e7aea2dbf9743a9a
- https://gist.github.com/b33t1e/e9e8192317c111e7897e04d2f9bf5fdb
- https://github.com/appwrite/appwrite
- https://notes.sjtu.edu.cn/gMNlpByZSDiwrl9uZyHTKA
- http://appwrite.com
