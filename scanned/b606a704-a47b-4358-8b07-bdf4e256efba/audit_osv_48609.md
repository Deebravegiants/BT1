# [M] CVE-2018-1000199

## Summary
Severity: Medium
Advisory: CVE-2018-1000199
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-05-24
Source: https://osv.dev/vulnerability/CVE-2018-1000199
Type: osv

## Details
The Linux Kernel version 3.18 contains a dangerous feature vulnerability in modify_user_hw_breakpoint() that can result in crash and possibly memory corruption. This attack appear to be exploitable via local code execution and the ability to use ptrace. This vulnerability appears to have been fixed in git commit f67b15037a7a50c57f72e69a6d59941ad90a0f0f.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00022.html
- https://access.redhat.com/errata/RHSA-2018:1347
- https://access.redhat.com/errata/RHSA-2018:1354
- https://usn.ubuntu.com/3641-1/
- https://access.redhat.com/errata/RHSA-2018:1318
- https://access.redhat.com/errata/RHSA-2018:1348
- https://usn.ubuntu.com/3641-2/
- https://www.debian.org/security/2018/dsa-4187
- http://www.securitytracker.com/id/1040806
- https://access.redhat.com/errata/RHSA-2018:1345
- https://access.redhat.com/errata/RHSA-2018:1355
- https://access.redhat.com/errata/RHSA-2018:1374
- https://lists.debian.org/debian-lts-announce/2018/05/msg00000.html
- https://www.debian.org/security/2018/dsa-4188
- https://lkml.org/lkml/2018/4/6/813
