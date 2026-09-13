# [C] tipc: fix double-free in tipc_buf_append()

## Summary
Severity: Critical
Advisory: CVE-2026-52993
Aliases: A-500022799, ASB-A-500022799
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52993
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

tipc: fix double-free in tipc_buf_append()

tipc_msg_validate() can potentially reallocate the skb it is validating,
freeing the old one.  In tipc_buf_append(), it was being called with a
pointer to a local variable which was a copy of the caller's skb
pointer.

If the skb was reallocated and validation subsequently failed, the error
handling path would free the original skb pointer, which had already
been freed, leading to double-free.

Fix this by checking if head now points to a newly allocated reassembled
skb.  If it does, reassign *headbuf for later freeing operations.

## References
- https://git.kernel.org/stable/c/0274f24485fc38032d4093e463dc3ff5c7a667c9
- https://git.kernel.org/stable/c/1d5e589055880fae229e229e1929e087dbe08cf3
- https://git.kernel.org/stable/c/29940fff14110ca48c5ccc168d121665b51bb778
- https://git.kernel.org/stable/c/4d104882bc815d4ec666ace9155f5f52715879a6
- https://git.kernel.org/stable/c/4ee4deadaae7cb2e3d53af0fc889cf92a73413c0
- https://git.kernel.org/stable/c/a438975a6dcdbd70865978c021650d1485586f0b
- https://git.kernel.org/stable/c/d293ca716e7d5dffdaecaf6b9b2f857a33dc3d3a
- https://git.kernel.org/stable/c/d3556656c6daebf8def751c7e71d11dd0a180d24
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-52993.json
- https://access.redhat.com/errata/RHSA-2026:45115
- https://access.redhat.com/errata/RHSA-2026:45116
- https://access.redhat.com/errata/RHSA-2026:47017
- https://access.redhat.com/errata/RHSA-2026:49212
- https://access.redhat.com/security/cve/CVE-2026-52993
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52993.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52993
- https://bugzilla.redhat.com/show_bug.cgi?id=2492437
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
