# [M] request-baskets vulnerable to Server-Side Request Forgery

## Summary
Severity: Medium
Advisory: GHSA-58g2-vgpg-335q
CVE: CVE-2023-27163
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-03-31
Source: https://github.com/advisories/GHSA-58g2-vgpg-335q
Type: github-advisory

## Affected
- Go: `github.com/darklynx/request-baskets` — affected >=0

## Details
request-baskets up to v1.2.1 was discovered to contain a Server-Side Request Forgery (SSRF) via the component /api/baskets/{name}. This vulnerability allows attackers to access network resources and sensitive information via a crafted API request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-27163
- https://gist.github.com/b33t1e/3079c10c88cad379fb166c389ce3b7b3
- https://github.com/darklynx/request-baskets
- https://notes.sjtu.edu.cn/s/MUUhEymt7
- http://packetstormsecurity.com/files/174128/Request-Baskets-1.2.1-Server-Side-Request-Forgery.html
- http://packetstormsecurity.com/files/174129/Maltrail-0.53-Remote-Code-Execution.html
- http://request-baskets.com
