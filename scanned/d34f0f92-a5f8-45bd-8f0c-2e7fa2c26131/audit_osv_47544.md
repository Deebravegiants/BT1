# [M] CVE-2016-7777

## Summary
Severity: Medium
Advisory: CVE-2016-7777
CVSS: 6.3 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2016-10-07
Source: https://osv.dev/vulnerability/CVE-2016-7777
Type: osv

## Details
Xen 4.7.x and earlier does not properly honor CR0.TS and CR0.EM, which allows local x86 HVM guest OS users to read or modify FPU, MMX, or XMM register state information belonging to arbitrary tasks on the guest by modifying an instruction while the hypervisor is preparing to emulate it.

## References
- https://support.citrix.com/article/CTX217363
- http://www.securitytracker.com/id/1036942
- https://security.gentoo.org/glsa/201611-09
- http://www.securityfocus.com/bid/93344
- http://xenbits.xen.org/xsa/advisory-190.html
