# [H] CVE-2016-9381

## Summary
Severity: High
Advisory: CVE-2016-9381
CVSS: 7.5 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2017-01-23
Source: https://osv.dev/vulnerability/CVE-2016-9381
Type: osv

## Details
Race condition in QEMU in Xen allows local x86 HVM guest OS administrators to gain privileges by changing certain data on shared rings, aka a "double fetch" vulnerability.

## References
- http://www.securityfocus.com/bid/94476
- http://www.securitytracker.com/id/1037344
- http://xenbits.xen.org/xsa/advisory-197.html
- https://security.gentoo.org/glsa/201612-56
- https://support.citrix.com/article/CTX218775
