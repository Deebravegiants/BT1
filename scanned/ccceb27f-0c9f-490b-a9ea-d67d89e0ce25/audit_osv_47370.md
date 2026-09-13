# [H] CVE-2016-3960

## Summary
Severity: High
Advisory: CVE-2016-3960
CVSS: 8.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2016-04-19
Source: https://osv.dev/vulnerability/CVE-2016-3960
Type: osv

## Details
Integer overflow in the x86 shadow pagetable code in Xen allows local guest OS users to cause a denial of service (host crash) or possibly gain privileges by shadowing a superpage mapping.

## References
- http://support.citrix.com/article/CTX209443
- http://www.securityfocus.com/bid/86318
- http://www.securitytracker.com/id/1035587
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/183275.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-May/184209.html
- http://www.oracle.com/technetwork/topics/security/ovmbulletinjul2016-3090546.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-May/183350.html
- http://www.debian.org/security/2016/dsa-3554
- http://xenbits.xen.org/xsa/advisory-173.html
