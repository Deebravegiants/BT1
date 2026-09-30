# [M] CVE-2023-4273

## Summary
Severity: Medium
Advisory: CVE-2023-4273
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-08-09
Source: https://osv.dev/vulnerability/CVE-2023-4273
Type: osv

## Details
A flaw was found in the exFAT driver of the Linux kernel. The vulnerability exists in the implementation of the file name reconstruction function, which is responsible for reading file name entries from a directory index and merging file name parts belonging to one file into a single long file name. Since the file name characters are copied into a stack variable, a local privileged attacker could use this flaw to overflow the kernel stack.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/3TYLSJ2SAI7RF56ZLQ5CQWCJLVJSD73Q/
- https://lists.debian.org/debian-lts-announce/2023/10/msg00027.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/344H6HO6SSC4KT7PDFXSDIXKMKHISSGF/
- https://www.debian.org/security/2023/dsa-5480
- https://access.redhat.com/security/cve/CVE-2023-4273
- https://www.debian.org/security/2023/dsa-5492
- https://access.redhat.com/errata/RHSA-2023:6583
- https://security.netapp.com/advisory/ntap-20231027-0002/
- https://bugzilla.redhat.com/show_bug.cgi?id=2221609
- https://dfir.ru/2023/08/23/cve-2023-4273-a-vulnerability-in-the-linux-exfat-driver/
