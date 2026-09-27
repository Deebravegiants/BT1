# [M] CVE-2016-9377

## Summary
Severity: Medium
Advisory: CVE-2016-9377
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-02-22
Source: https://osv.dev/vulnerability/CVE-2016-9377
Type: osv

## Details
Xen 4.5.x through 4.7.x on AMD systems without the NRip feature, when emulating instructions that generate software interrupts, allows local HVM guest OS users to cause a denial of service (guest crash) by leveraging IDT entry miscalculation.

## References
- http://www.securityfocus.com/bid/94475
- http://www.securitytracker.com/id/1037345
- https://security.gentoo.org/glsa/201612-56
- http://xenbits.xen.org/xsa/advisory-196.html
