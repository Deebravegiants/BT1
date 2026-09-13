# [H] CVE-2018-3848

## Summary
Severity: High
Advisory: CVE-2018-3848
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-04-16
Source: https://osv.dev/vulnerability/CVE-2018-3848
Type: osv

## Details
In the ffghbn function in NASA CFITSIO 3.42, specially crafted images parsed via the library can cause a stack-based buffer overflow overwriting arbitrary data. An attacker can deliver an FIT image to trigger this vulnerability and potentially gain code execution.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/K46I2MFPCEOGC5LLDXZSWPB3EBPON3KA/
- https://security.gentoo.org/glsa/202101-24
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2018-0531
