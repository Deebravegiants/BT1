# [H] CVE-2017-14319

## Summary
Severity: High
Advisory: CVE-2017-14319
CVSS: 8.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2017-09-12
Source: https://osv.dev/vulnerability/CVE-2017-14319
Type: osv

## Details
A grant unmapping issue was discovered in Xen through 4.9.x. When removing or replacing a grant mapping, the x86 PV specific path needs to make sure page table entries remain in sync with other accounting done. Although the identity of the page frame was validated correctly, neither the presence of the mapping nor page writability were taken into account.

## References
- https://lists.debian.org/debian-lts-announce/2018/10/msg00009.html
- https://support.citrix.com/article/CTX227185
- http://www.securityfocus.com/bid/100819
- http://www.securitytracker.com/id/1039351
- https://www.debian.org/security/2017/dsa-4050
- http://xenbits.xen.org/xsa/advisory-234.html
