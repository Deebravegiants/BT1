# [H] mpls: add seqcount to protect the platform_label{,s} pair

## Summary
Severity: High
Advisory: CVE-2026-43042
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-43042
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.1.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

mpls: add seqcount to protect the platform_label{,s} pair

The RCU-protected codepaths (mpls_forward, mpls_dump_routes) can have
an inconsistent view of platform_labels vs platform_label in case of a
concurrent resize (resize_platform_label_table, under
platform_mutex). This can lead to OOB accesses.

This patch adds a seqcount, so that we get a consistent snapshot.

Note that mpls_label_ok is also susceptible to this, so the check
against RTA_DST in rtm_to_route_config, done outside platform_mutex,
is not sufficient. This value gets passed to mpls_label_ok once more
in both mpls_route_add and mpls_route_del, so there is no issue, but
that additional check must not be removed.

## References
- https://git.kernel.org/stable/c/5bb3caf0bbfb56f1a00d2af072ac3d8395a3b9ef
- https://git.kernel.org/stable/c/629ec78ef8608d955ce217880cdc3e1873af3a15
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43042.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43042
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
