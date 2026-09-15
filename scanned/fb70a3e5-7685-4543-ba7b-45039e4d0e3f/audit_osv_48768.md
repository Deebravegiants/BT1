# [M] CVE-2018-12893

## Summary
Severity: Medium
Advisory: CVE-2018-12893
CVSS: 6.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2018-07-02
Source: https://osv.dev/vulnerability/CVE-2018-12893
Type: osv

## Details
An issue was discovered in Xen through 4.10.x. One of the fixes in XSA-260 added some safety checks to help prevent Xen livelocking with debug exceptions. Unfortunately, due to an oversight, at least one of these safety checks can be triggered by a guest. A malicious PV guest can crash Xen, leading to a Denial of Service. All Xen systems which have applied the XSA-260 fix are vulnerable. Only x86 systems are vulnerable. ARM systems are not vulnerable. Only x86 PV guests can exploit the vulnerability. x86 HVM and PVH guests cannot exploit the vulnerability. An attacker needs to be able to control hardware debugging facilities to exploit the vulnerability, but such permissions are typically available to unprivileged users.

## References
- https://lists.debian.org/debian-lts-announce/2018/11/msg00013.html
- https://security.gentoo.org/glsa/201810-06
- http://www.securitytracker.com/id/1041202
- https://support.citrix.com/article/CTX235748
- https://www.debian.org/security/2018/dsa-4236
- http://www.securityfocus.com/bid/104572
- https://bugzilla.redhat.com/show_bug.cgi?id=1590979
- http://www.openwall.com/lists/oss-security/2018/06/27/11
- http://xenbits.xen.org/xsa/advisory-265.html
