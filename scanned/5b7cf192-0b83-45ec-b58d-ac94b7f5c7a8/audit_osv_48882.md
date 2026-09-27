# [H] CVE-2018-16884

## Summary
Severity: High
Advisory: CVE-2018-16884
CVSS: 8.0 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-18
Source: https://osv.dev/vulnerability/CVE-2018-16884
Type: osv

## Details
A flaw was found in the Linux kernel's NFS41+ subsystem. NFS41+ shares mounted in different network namespaces at the same time can make bc_svc_process() use wrong back-channel IDs and cause a use-after-free vulnerability. Thus a malicious container user can cause a host kernel memory corruption and a system panic. Due to the nature of the flaw, privilege escalation cannot be fully ruled out.

## References
- https://access.redhat.com/errata/RHSA-2019:2730
- https://lists.debian.org/debian-lts-announce/2019/03/msg00034.html
- https://usn.ubuntu.com/3981-2/
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://access.redhat.com/errata/RHSA-2019:1891
- https://access.redhat.com/errata/RHSA-2019:3309
- https://usn.ubuntu.com/3981-1/
- https://access.redhat.com/errata/RHSA-2019:1873
- https://lists.debian.org/debian-lts-announce/2019/04/msg00004.html
- https://access.redhat.com/errata/RHSA-2019:3517
- https://access.redhat.com/errata/RHSA-2020:0204
- https://lists.debian.org/debian-lts-announce/2019/05/msg00002.html
- https://support.f5.com/csp/article/K21430012
- https://usn.ubuntu.com/3932-1/
- https://usn.ubuntu.com/3932-2/
- https://usn.ubuntu.com/3980-1/
- https://usn.ubuntu.com/3980-2/
- http://www.securityfocus.com/bid/106253
- https://access.redhat.com/errata/RHSA-2019:2696
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-16884
