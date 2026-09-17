# [M] CVE-2024-0564

## Summary
Severity: Medium
Advisory: CVE-2024-0564
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-01-30
Source: https://osv.dev/vulnerability/CVE-2024-0564
Type: osv

## Details
A flaw was found in the Linux kernel's memory deduplication mechanism. The max page sharing of Kernel Samepage Merging (KSM), added in Linux kernel version 4.4.0-96.119, can create a side channel. When the attacker and the victim share the same host and the default setting of KSM is "max page sharing=256", it is possible for the attacker to time the unmap to merge with the victim's page. The unmapping time depends on whether it merges with the victim's page and additional physical pages are created beyond the KSM's "max page share". Through these operations, the attacker can leak the victim's page.

## References
- https://link.springer.com/conference/wisa
- https://wisa.or.kr/accepted
- https://access.redhat.com/security/cve/CVE-2024-0564
- https://bugs.launchpad.net/ubuntu/+source/linux/+bug/1680513
- https://bugzilla.redhat.com/show_bug.cgi?id=2258514
