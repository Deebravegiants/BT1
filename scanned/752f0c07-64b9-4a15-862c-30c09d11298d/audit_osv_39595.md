# [C] netfilter: nft_inner: Fix IPv6 inner_thoff desync

## Summary
Severity: Critical
Advisory: CVE-2026-46244
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-06-03
Source: https://osv.dev/vulnerability/CVE-2026-46244
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nft_inner: Fix IPv6 inner_thoff desync

In nft_inner_parse_l2l3(), when processing inner IPv6 packets,
ipv6_find_hdr() correctly computes the transport header offset
traversing all extension headers, but the result is immediately
overwritten with nhoff + sizeof(_ip6h) (40 bytes), which only
accounts for the IPv6 base header. This creates a desync between
inner_thoff (wrong — points to extension header start) and l4proto
(correct — e.g., IPPROTO_TCP), enabling transport header forgery
and potential firewall bypass. This issue affects stable versions
from Linux 6.2.

For comparison, the normal (non-inner) IPv6 path correctly
preserves ipv6_find_hdr()'s result. Removing the incorrect overwrite
ensures that ipv6_find_hdr()'s calculated transport header offset is
preserved, thereby fixing the desynchronization.

## References
- https://git.kernel.org/stable/c/689bbf48c1f45130086ae1c46ab83ea4c753c601
- https://git.kernel.org/stable/c/870d59e2cf218e7418491e26bad768cb16654582
- https://git.kernel.org/stable/c/b6a91f68ebfed9c38e0e9150f58a9b85da07181c
- https://git.kernel.org/stable/c/c161ad9157f5a0429b5ff94d9770faf3bf48d273
- https://git.kernel.org/stable/c/d0f98a3617f6ae5b1e95cde1e68e7ead4a1279ce
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-46244.json
- https://access.redhat.com/errata/RHSA-2026:33215
- https://access.redhat.com/errata/RHSA-2026:34094
- https://access.redhat.com/errata/RHSA-2026:34443
- https://access.redhat.com/errata/RHSA-2026:34911
- https://access.redhat.com/errata/RHSA-2026:36018
- https://access.redhat.com/errata/RHSA-2026:55618
- https://access.redhat.com/errata/RHSA-2026:55763
- https://access.redhat.com/errata/RHSA-2026:56225
- https://access.redhat.com/security/cve/CVE-2026-46244
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46244.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46244
- https://bugzilla.redhat.com/show_bug.cgi?id=2484451
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
