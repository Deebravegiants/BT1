# [M] CVE-2018-7540

## Summary
Severity: Medium
Advisory: CVE-2018-7540
CVSS: 6.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2018-02-27
Source: https://osv.dev/vulnerability/CVE-2018-7540
Type: osv

## Details
An issue was discovered in Xen through 4.10.x allowing x86 PV guest OS users to cause a denial of service (host OS CPU hang) via non-preemptable L3/L4 pagetable freeing.

## References
- https://support.citrix.com/article/CTX232096
- http://www.securityfocus.com/bid/103174
- http://www.securitytracker.com/id/1040773
- https://lists.debian.org/debian-lts-announce/2018/11/msg00013.html
- https://support.citrix.com/article/CTX232655
- https://lists.debian.org/debian-lts-announce/2018/03/msg00003.html
- https://security.gentoo.org/glsa/201810-06
- https://xenbits.xen.org/xsa/advisory-252.html
- https://www.debian.org/security/2018/dsa-4131
