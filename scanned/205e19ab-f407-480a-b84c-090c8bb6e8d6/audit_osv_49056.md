# [H] CVE-2018-3847

## Summary
Severity: High
Advisory: CVE-2018-3847
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-08-01
Source: https://osv.dev/vulnerability/CVE-2018-3847
Type: osv

## Details
Multiple exploitable buffer overflow vulnerabilities exist in image parsing functionality of the CFITSIO library version 3.42. Specially crafted images parsed via the library, can cause a stack-based buffer overflow overwriting arbitrary data. An attacker can deliver an FIT image to trigger this vulnerability and potentially gain code execution.

## References
- https://security.gentoo.org/glsa/202101-24
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2018-0530
