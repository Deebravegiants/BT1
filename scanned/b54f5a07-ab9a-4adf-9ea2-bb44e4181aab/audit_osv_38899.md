# [H] netfilter: ctnetlink: ignore explicit helper on new expectations

## Summary
Severity: High
Advisory: CVE-2026-43025
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-43025
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.12.0 <6.1.168, >=6.2.0 <6.6.134, >=6.7.0 <6.12.81, >=6.13.0 <6.18.22, >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: ctnetlink: ignore explicit helper on new expectations

Use the existing master conntrack helper, anything else is not really
supported and it just makes validation more complicated, so just ignore
what helper userspace suggests for this expectation.

This was uncovered when validating CTA_EXPECT_CLASS via different helper
provided by userspace than the existing master conntrack helper:

  BUG: KASAN: slab-out-of-bounds in nf_ct_expect_related_report+0x2479/0x27c0
  Read of size 4 at addr ffff8880043fe408 by task poc/102
  Call Trace:
   nf_ct_expect_related_report+0x2479/0x27c0
   ctnetlink_create_expect+0x22b/0x3b0
   ctnetlink_new_expect+0x4bd/0x5c0
   nfnetlink_rcv_msg+0x67a/0x950
   netlink_rcv_skb+0x120/0x350

Allowing to read kernel memory bytes off the expectation boundary.

CTA_EXPECT_HELP_NAME is still used to offer the helper name to userspace
via netlink dump.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/0f6c33697ccfac6499d0b7a4dbdec5d3a3a566cd
- https://git.kernel.org/stable/c/187b6ec5229ea93cb04c4f6d3b52efc80f513d0d
- https://git.kernel.org/stable/c/21a04c31db4057deec85fcd6cc63d720b38819c3
- https://git.kernel.org/stable/c/2ea0f35f235f70c133ad61fe05ba013753b978c6
- https://git.kernel.org/stable/c/917b61fa2042f11e2af4c428e43f08199586633a
- https://git.kernel.org/stable/c/e135f8e8212cbed12a03ab8dec77fa1247139897
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43025.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43025
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
