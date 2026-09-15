# [H] CVE-2021-22543

## Summary
Severity: High
Advisory: CVE-2021-22543
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-26
Source: https://osv.dev/vulnerability/CVE-2021-22543
Type: osv

## Details
An issue was discovered in Linux: KVM through Improper handling of VM_IO|VM_PFNMAP vmas in KVM can bypass RO checks and can lead to pages being freed while still accessible by the VMM and guest. This allows users with the ability to start and control a VM to read/write random pages of memory and can result in local privilege escalation.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4G5YBUVEPHZYXMKNGBZ3S6INFCTEEL4E/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ROQIXQB7ZAWI3KSGSHR6H5RDUWZI775S/
- https://security.netapp.com/advisory/ntap-20210708-0002/
- https://lists.debian.org/debian-lts-announce/2021/10/msg00010.html
- https://lists.debian.org/debian-lts-announce/2021/12/msg00012.html
- http://www.openwall.com/lists/oss-security/2021/06/26/1
- https://github.com/google/security-research/security/advisories/GHSA-7wq5-phmq-m584
