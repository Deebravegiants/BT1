# [M] CVE-2019-5188

## Summary
Severity: Medium
Advisory: CVE-2019-5188
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-01-08
Source: https://osv.dev/vulnerability/CVE-2019-5188
Type: osv

## Details
A code execution vulnerability exists in the directory rehashing functionality of E2fsprogs e2fsck 1.45.4. A specially crafted ext4 directory can cause an out-of-bounds write on the stack, resulting in code execution. An attacker can corrupt a partition to trigger this vulnerability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2AKETJ6BREDUHRWQTV35SPGG5C6H7KSI/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6DOBCYQKCTTWXBLMUPJ5TX3FY7JNCOKY/
- http://lists.opensuse.org/opensuse-security-announce/2020-02/msg00004.html
- https://lists.debian.org/debian-lts-announce/2020/03/msg00030.html
- https://lists.debian.org/debian-lts-announce/2020/07/msg00021.html
- https://security.netapp.com/advisory/ntap-20220506-0001/
- https://usn.ubuntu.com/4249-1/
- https://talosintelligence.com/vulnerability_reports/TALOS-2019-0973
