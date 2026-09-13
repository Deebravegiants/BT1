# [H] CVE-2017-14450

## Summary
Severity: High
Advisory: CVE-2017-14450
CVSS: 7.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:H)
Published: 2018-04-24
Source: https://osv.dev/vulnerability/CVE-2017-14450
Type: osv

## Details
A buffer overflow vulnerability exists in the GIF image parsing functionality of SDL2_image-2.0.2. A specially crafted GIF image can lead to a buffer overflow on a global section. An attacker can display an image to trigger this vulnerability.

## References
- https://www.debian.org/security/2018/dsa-4177
- https://www.debian.org/security/2018/dsa-4184
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2017-0499
- https://lists.debian.org/debian-lts-announce/2018/04/msg00005.html
- https://security.gentoo.org/glsa/201903-17
