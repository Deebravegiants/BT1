# [M] EC-CUBE Cross-site request forgery (CSRF) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-m9hv-qmqh-33qh
CVE: CVE-2021-20842
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-m9hv-qmqh-33qh
Type: github-advisory

## Affected
- Packagist: `ec-cube/ec-cube` — affected >=2.11.0 <2.17.2

## Details
Cross-site request forgery (CSRF) vulnerability in EC-CUBE 2 series 2.11.0 to 2.17.1 allows a remote attacker to hijack the authentication of Administrator and delete Administrator via a specially crafted web page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-20842
- https://github.com/EC-CUBE/ec-cube
- https://jvn.jp/en/jp/JVN75444925/index.html
- https://www.ec-cube.net/info/weakness/20211111
