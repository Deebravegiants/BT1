# [C] netfilter: conntrack: remove sprintf usage

## Summary
Severity: Critical
Advisory: CVE-2026-53002
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53002
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.20 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: conntrack: remove sprintf usage

Replace it with scnprintf, the buffer sizes are expected to be large enough
to hold the result, no need for snprintf+overflow check.

Increase buffer size in mangle_content_len() while at it.

BUG: KASAN: stack-out-of-bounds in vsnprintf+0xea5/0x1270
Write of size 1 at addr [..]
 vsnprintf+0xea5/0x1270
 sprintf+0xb1/0xe0
 mangle_content_len+0x1ac/0x280
 nf_nat_sdp_session+0x1cc/0x240
 process_sdp+0x8f8/0xb80
 process_invite_request+0x108/0x2b0
 process_sip_msg+0x5da/0xf50
 sip_help_tcp+0x45e/0x780
 nf_confirm+0x34d/0x990
 [..]

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/1c9fb8aeed06790d42cdcd00f6c3ce0b9e926c1e
- https://git.kernel.org/stable/c/2f793ba78470a99f40389b7dc60a81d9f5ad3956
- https://git.kernel.org/stable/c/6bbf829b4c1b44c941c47dd0d710f1393258f3d5
- https://git.kernel.org/stable/c/6e7066bdb481a87fe88c4fa563e348c03b2d373d
- https://git.kernel.org/stable/c/8e3be0d12615a173fe260cd42753ca7a001acbf2
- https://git.kernel.org/stable/c/a8e0a32a23d3f34862af3b4da792ecb3a891a9a3
- https://git.kernel.org/stable/c/ab64e61c9323fa6de21bd20da1ddb29a0fb65d34
- https://git.kernel.org/stable/c/c08ff52e44945e6ef4ce0790f49ea761b060c45b
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-53002.json
- https://access.redhat.com/errata/RHSA-2026:64770
- https://access.redhat.com/errata/RHSA-2026:66000
- https://access.redhat.com/errata/RHSA-2026:66180
- https://access.redhat.com/security/cve/CVE-2026-53002
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53002.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53002
- https://bugzilla.redhat.com/show_bug.cgi?id=2492329
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
