# [H] CVE-2018-3977

## Summary
Severity: High
Advisory: CVE-2018-3977
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-11-01
Source: https://osv.dev/vulnerability/CVE-2018-3977
Type: osv

## Details
An exploitable code execution vulnerability exists in the XCF image rendering functionality of SDL2_image-2.0.3. A specially crafted XCF image can cause a heap overflow, resulting in code execution. An attacker can display a specially crafted image to trigger this vulnerability.

## References
- https://usn.ubuntu.com/4238-1/
- https://lists.debian.org/debian-lts-announce/2019/07/msg00021.html
- https://lists.debian.org/debian-lts-announce/2019/07/msg00026.html
- https://security.gentoo.org/glsa/201903-17
- https://talosintelligence.com/vulnerability_reports/TALOS-2018-0645
