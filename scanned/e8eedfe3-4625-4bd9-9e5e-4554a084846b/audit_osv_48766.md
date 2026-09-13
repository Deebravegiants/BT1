# [M] CVE-2018-12891

## Summary
Severity: Medium
Advisory: CVE-2018-12891
CVSS: 6.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2018-07-02
Source: https://osv.dev/vulnerability/CVE-2018-12891
Type: osv

## Details
An issue was discovered in Xen through 4.10.x. Certain PV MMU operations may take a long time to process. For that reason Xen explicitly checks for the need to preempt the current vCPU at certain points. A few rarely taken code paths did bypass such checks. By suitably enforcing the conditions through its own page table contents, a malicious guest may cause such bypasses to be used for an unbounded number of iterations. A malicious or buggy PV guest may cause a Denial of Service (DoS) affecting the entire host. Specifically, it may prevent use of a physical CPU for an indeterminate period of time. All Xen versions from 3.4 onwards are vulnerable. Xen versions 3.3 and earlier are vulnerable to an even wider class of attacks, due to them lacking preemption checks altogether in the affected code paths. Only x86 systems are affected. ARM systems are not affected. Only multi-vCPU x86 PV guests can leverage the vulnerability. x86 HVM or PVH guests as well as x86 single-vCPU PV ones cannot leverage the vulnerability.

## References
- http://www.securitytracker.com/id/1041201
- https://security.gentoo.org/glsa/201810-06
- https://support.citrix.com/article/CTX235748
- https://www.debian.org/security/2018/dsa-4236
- http://www.securityfocus.com/bid/104570
- https://lists.debian.org/debian-lts-announce/2018/11/msg00013.html
- http://xenbits.xen.org/xsa/advisory-264.html
- http://www.openwall.com/lists/oss-security/2018/06/27/10
