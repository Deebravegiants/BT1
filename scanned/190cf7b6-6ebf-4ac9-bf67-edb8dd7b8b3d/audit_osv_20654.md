# [H] CVE-2021-3571

## Summary
Severity: High
Advisory: CVE-2021-3571
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:H)
Published: 2021-07-09
Source: https://osv.dev/vulnerability/CVE-2021-3571
Type: osv

## Details
A flaw was found in the ptp4l program of the linuxptp package. When ptp4l is operating on a little-endian architecture as a PTP transparent clock, a remote attacker could send a crafted one-step sync message to cause an information leak or crash. The highest threat from this vulnerability is to data confidentiality and system availability. This flaw affects linuxptp versions before 3.1.1 and before 2.0.1.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RHRUVSDP673LXJ5HGIPQPWPIYUPWYQA7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VUBKTRCMJ6VKS7DIBSZQB4ATSKVCJYXJ/
- https://bugzilla.redhat.com/show_bug.cgi?id=1966241
