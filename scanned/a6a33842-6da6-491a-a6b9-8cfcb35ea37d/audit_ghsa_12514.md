# [C] Microcks contains a Server-Side Request Forgery (SSRF) via the component /jobs and /artifact/download

## Summary
Severity: Critical
Advisory: GHSA-gqj2-324p-vx73
CVE: CVE-2023-48910
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-12-04
Source: https://github.com/advisories/GHSA-gqj2-324p-vx73
Type: github-advisory

## Affected
- Maven: `io.github.microcks:microcks` — affected >=0 <1.17.1

## Details
Microcks up to version 1.17.1 was discovered to contain a Server-Side Request Forgery (SSRF) via the component /jobs and /artifact/download. This vulnerability allows attackers to access network resources and sensitive information via a crafted GET request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-48910
- https://gist.github.com/b33t1e/2a2dc17cf36cd741b2c99425c892d826
- https://github.com/microcks/microcks
- https://github.com/orgs/microcks/discussions/892
