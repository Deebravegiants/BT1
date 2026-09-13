# [H] CVE-2017-2920

## Summary
Severity: High
Advisory: CVE-2017-2920
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-10-05
Source: https://osv.dev/vulnerability/CVE-2017-2920
Type: osv

## Details
An memory corruption vulnerability exists in the .SVG parsing functionality of Computerinsel Photoline 20.02. A specially crafted .SVG file can cause a vulnerability resulting in memory corruption, which can potentially lead to arbitrary code execution. An attacker can send a specific .SVG file to trigger this vulnerability.

## References
- http://www.securityfocus.com/bid/101186
- https://security.gentoo.org/glsa/201908-26
- https://github.com/libofx/libofx/commit/a70934eea95c76a7737b83773bffe8738935082d
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2017-0427
