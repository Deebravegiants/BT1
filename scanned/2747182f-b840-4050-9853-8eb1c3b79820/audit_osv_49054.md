# [H] CVE-2018-3839

## Summary
Severity: High
Advisory: CVE-2018-3839
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-04-10
Source: https://osv.dev/vulnerability/CVE-2018-3839
Type: osv

## Details
An exploitable code execution vulnerability exists in the XCF image rendering functionality of Simple DirectMedia Layer SDL2_image-2.0.2. A specially crafted XCF image can cause an out-of-bounds write on the heap, resulting in code execution. An attacker can display a specially crafted image to trigger this vulnerability.

## References
- https://security.gentoo.org/glsa/201903-17
- https://www.debian.org/security/2018/dsa-4177
- https://www.debian.org/security/2018/dsa-4184
- https://www.starwindsoftware.com/security/sw-20191008-0002/
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2018-0521
