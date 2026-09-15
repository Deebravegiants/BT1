# [C] CVE-2018-12976

## Summary
Severity: Critical
Advisory: CVE-2018-12976
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-05
Source: https://osv.dev/vulnerability/CVE-2018-12976
Type: osv

## Details
In Go Doc Dot Org (gddo) through 2018-06-27, an attacker could use specially crafted <go-import> tags in packages being fetched by gddo to cause a directory traversal and remote code execution.

## References
- https://groups.google.com/forum/#%21msg/golang-announce/4rpTbfzYB1k/no6MEwlQAwAJ
- https://github.com/golang/gddo/commit/daffe1f90ec57f8ed69464f9094753fc6452e983
