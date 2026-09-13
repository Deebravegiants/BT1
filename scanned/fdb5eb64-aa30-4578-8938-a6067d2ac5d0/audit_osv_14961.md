# [H] CVE-2019-12589

## Summary
Severity: High
Advisory: CVE-2019-12589
CVSS: 8.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2019-06-03
Source: https://osv.dev/vulnerability/CVE-2019-12589
Type: osv

## Details
In Firejail before 0.9.60, seccomp filters are writable inside the jail, leading to a lack of intended seccomp restrictions for a process that is joined to the jail after a filter has been modified by an attacker.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CDY7B73YDRBURA25APSHD5PFEO4TNSFW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RGVULJ6IKVDO6UAVIQRHQVSKOUD6QDWM/
- https://github.com/netblue30/firejail/releases/tag/0.9.60
- https://github.com/netblue30/firejail/commit/eecf35c2f8249489a1d3e512bb07f0d427183134
- https://github.com/netblue30/firejail/issues/2718
