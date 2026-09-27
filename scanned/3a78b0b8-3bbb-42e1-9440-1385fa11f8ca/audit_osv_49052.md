# [M] CVE-2018-3837

## Summary
Severity: Medium
Advisory: CVE-2018-3837
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2018-04-10
Source: https://osv.dev/vulnerability/CVE-2018-3837
Type: osv

## Details
An exploitable information disclosure vulnerability exists in the PCX image rendering functionality of Simple DirectMedia Layer SDL2_image-2.0.2. A specially crafted PCX image can cause an out-of-bounds read on the heap, resulting in information disclosure . An attacker can display a specially crafted image to trigger this vulnerability.

## References
- https://security.gentoo.org/glsa/201903-17
- https://www.debian.org/security/2018/dsa-4177
- https://www.debian.org/security/2018/dsa-4184
- https://www.starwindsoftware.com/security/sw-20191008-0001/
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2018-0519
