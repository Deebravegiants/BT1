# [H] Path traversal in Gitblit

## Summary
Severity: High
Advisory: GHSA-2c65-rq62-fqhq
CVE: CVE-2022-31268
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-22
Source: https://github.com/advisories/GHSA-2c65-rq62-fqhq
Type: github-advisory

## Affected
- Maven: `com.gitblit:gitblit` — affected >=0

## Details
A Path Traversal vulnerability in Gitblit 1.9.3 can lead to reading website files via /resources//../ (e.g., followed by a WEB-INF or META-INF pathname).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-31268
- https://github.com/gitblit/gitblit
- https://github.com/metaStor/Vuls/blob/main/gitblit/gitblit%20V1.9.3%20path%20traversal/gitblit%20V1.9.3%20path%20traversal.md
