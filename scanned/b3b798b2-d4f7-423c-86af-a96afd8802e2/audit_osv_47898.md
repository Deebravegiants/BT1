# [H] CVE-2017-14448

## Summary
Severity: High
Advisory: CVE-2017-14448
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-04-24
Source: https://osv.dev/vulnerability/CVE-2017-14448
Type: osv

## Details
An exploitable code execution vulnerability exists in the XCF image rendering functionality of SDL2_image-2.0.2. A specially crafted XCF image can cause a heap overflow resulting in code execution. An attacker can display a specially crafted image to trigger this vulnerability.

## References
- https://lists.debian.org/debian-lts-announce/2018/04/msg00005.html
- https://security.gentoo.org/glsa/201903-17
- https://www.debian.org/security/2018/dsa-4177
- https://www.debian.org/security/2018/dsa-4184
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2017-0497
