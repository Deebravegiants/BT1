# [H] Moderate: kernel security update

## Summary
Severity: High
Advisory: RXSA-2026:3488
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-21
Source: https://osv.dev/vulnerability/RXSA-2026:3488
Type: osv

## Details
The kernel packages contain the Linux kernel, the core of any Linux operating system.

Security Fix(es):

* kernel: smc: Use __sk_dst_get() and dst_dev_rcu() in smc_clc_prfx_match() (CVE-2025-40168)

* kernel: ipv6: BUG() in pskb_expand_head() as part of calipso_skbuff_setattr() (CVE-2025-71085)

* kernel: Linux kernel: Denial of Service due to a deadlock in hugetlb folio migration (CVE-2026-23097)

For more details about the security issue(s), including the impact, a CVSS score, acknowledgments, and other related information, refer to the CVE page(s) listed in the References section.

## References
- https://errata.rockylinux.org/RXSA-2026:3488
- https://bugzilla.redhat.com/show_bug.cgi?id=2414482
- https://bugzilla.redhat.com/show_bug.cgi?id=2429026
- https://bugzilla.redhat.com/show_bug.cgi?id=2436802
