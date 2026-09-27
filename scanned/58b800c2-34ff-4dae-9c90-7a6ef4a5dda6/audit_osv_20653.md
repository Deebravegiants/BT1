# [H] CVE-2021-3570

## Summary
Severity: High
Advisory: CVE-2021-3570
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-07-09
Source: https://osv.dev/vulnerability/CVE-2021-3570
Type: osv

## Details
A flaw was found in the ptp4l program of the linuxptp package. A missing length check when forwarding a PTP message between ports allows a remote attacker to cause an information leak, crash, or potentially remote code execution. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability. This flaw affects linuxptp versions before 3.1.1, before 2.0.1, before 1.9.3, before 1.8.1, before 1.7.1, before 1.6.1 and before 1.5.1.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RHRUVSDP673LXJ5HGIPQPWPIYUPWYQA7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VUBKTRCMJ6VKS7DIBSZQB4ATSKVCJYXJ/
- https://lists.debian.org/debian-lts-announce/2021/07/msg00025.html
- https://www.debian.org/security/2021/dsa-4938
- https://bugzilla.redhat.com/show_bug.cgi?id=1966240
