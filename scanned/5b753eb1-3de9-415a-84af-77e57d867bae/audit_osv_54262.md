# [M] CVE-2023-4569

## Summary
Severity: Medium
Advisory: CVE-2023-4569
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-08-28
Source: https://osv.dev/vulnerability/CVE-2023-4569
Type: osv

## Details
A memory leak flaw was found in nft_set_catchall_flush in net/netfilter/nf_tables_api.c in the Linux Kernel. This issue may allow a local attacker to cause double-deactivations of catchall elements, which can result in a memory leak.

## References
- https://access.redhat.com/security/cve/CVE-2023-4569
- https://www.debian.org/security/2023/dsa-5492
- https://bugzilla.redhat.com/show_bug.cgi?id=2235470
- https://patchwork.ozlabs.org/project/netfilter-devel/patch/20230812110526.49808-1-fw@strlen.de/
