# [H] Flask is vulnerable to Denial of Service via incorrect encoding of JSON data

## Summary
Severity: High
Advisory: GHSA-562c-5r94-xh97
CVE: CVE-2018-1000656
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-08-23
Source: https://github.com/advisories/GHSA-562c-5r94-xh97
Type: github-advisory

## Affected
- PyPI: `Flask` — affected >=0 <0.12.3

## Details
The Pallets Project flask version Before 0.12.3 contains a CWE-20: Improper Input Validation vulnerability in flask that can result in Large amount of memory usage possibly leading to denial of service. This attack appear to be exploitable via Attacker provides JSON data in incorrect encoding. This vulnerability appears to have been fixed in 0.12.3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000656
- https://github.com/pallets/flask/pull/2691
- https://github.com/pallets/flask/commit/b178e89e4456e777b1a7ac6d7199052d0dfdbbbe
- https://github.com/advisories/GHSA-562c-5r94-xh97
- https://github.com/pallets/flask
- https://github.com/pallets/flask/releases/tag/0.12.3
- https://github.com/pypa/advisory-database/tree/main/vulns/flask/PYSEC-2018-66.yaml
- https://lists.debian.org/debian-lts-announce/2019/08/msg00025.html
- https://security.netapp.com/advisory/ntap-20190221-0001
- https://usn.ubuntu.com/4378-1
