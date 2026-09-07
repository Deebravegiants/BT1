# [M] EC-CUBE DOM-based cross-site scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-pggw-rqfm-72rh
CVE: CVE-2022-38975
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-09-28
Source: https://github.com/advisories/GHSA-pggw-rqfm-72rh
Type: github-advisory

## Affected
- Packagist: `ec-cube/ec-cube` — affected >=4.0.0

## Details
DOM-based cross-site scripting vulnerability in EC-CUBE 4 series (EC-CUBE 4.0.0 to 4.1.2) allows a remote attacker to inject an arbitrary script by having an administrative user of the product to visit a specially crafted page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-38975
- https://github.com/EC-CUBE/ec-cube
- https://jvn.jp/en/jp/JVN21213852/index.html
- https://www.ec-cube.net/info/weakness/20220909
