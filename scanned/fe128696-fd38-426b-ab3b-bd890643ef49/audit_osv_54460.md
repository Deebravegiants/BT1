# [M] CVE-2023-6622

## Summary
Severity: Medium
Advisory: CVE-2023-6622
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-12-08
Source: https://osv.dev/vulnerability/CVE-2023-6622
Type: osv

## Details
A null pointer dereference vulnerability was found in nft_dynset_init() in net/netfilter/nft_dynset.c in nf_tables in the Linux kernel. This issue may allow a local attacker with CAP_NET_ADMIN user privilege to trigger a denial of service.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/AAOVK2F3ALGKYIQ5IOMAYEC2DGI7BWAW/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/G3AGDVE3KBLOOYBPISFDS74R4YAZEDAY/
- https://access.redhat.com/errata/RHSA-2024:2394
- https://access.redhat.com/errata/RHSA-2024:2950
- https://access.redhat.com/errata/RHSA-2024:3138
- https://access.redhat.com/security/cve/CVE-2023-6622
- https://bugzilla.redhat.com/show_bug.cgi?id=2253632
- https://github.com/torvalds/linux/commit/3701cd390fd731ee7ae8b8006246c8db82c72bea
