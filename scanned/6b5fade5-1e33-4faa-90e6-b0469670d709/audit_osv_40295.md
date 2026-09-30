# [H] netfilter: ip6t_hbh: reject oversized option lists

## Summary
Severity: High
Advisory: CVE-2026-52915
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52915
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: ip6t_hbh: reject oversized option lists

struct ip6t_opts stores at most IP6T_OPTS_OPTSNR option descriptors,
but hbh_mt6_check() does not reject larger optsnr values supplied from
userspace.

Validate optsnr in the rule setup path so only match data that fits the
fixed-size opts array can be installed. This follows the existing xtables
pattern of rejecting invalid user-provided counts in checkentry() and
keeps the packet matching path unchanged.

`struct ip6t_opts` has a fixed `opts[IP6T_OPTS_OPTSNR]` array,
where `IP6T_OPTS_OPTSNR` is 16, then off-by-one array access is possible:

[  137.924693][ T8692] UBSAN: array-index-out-of-bounds in ../net/ipv6/netfilter/ip6t_hbh.c:110:29
[  137.926167][ T8692] index 16 is out of range for type '__u16 [16]'

## References
- https://git.kernel.org/stable/c/2d523ba48d4ecc46acfb6aba548292cfcce1ac02
- https://git.kernel.org/stable/c/41ec2e242f1702e8370ddfe14d22b7a766021c3e
- https://git.kernel.org/stable/c/4322dcde6b4173c2d8e8e6118ed290794263bcc8
- https://git.kernel.org/stable/c/57b0ac5e1b46f1f0338dff392ef2092e2871b412
- https://git.kernel.org/stable/c/588933f1a2ca5ff99274f8c9f25dc3a25d0191c3
- https://git.kernel.org/stable/c/6feb43c0995ab3a9c826707eb46541a1696fe4f7
- https://git.kernel.org/stable/c/784aadea7a108c9f90985683caa87fb0198c6a39
- https://git.kernel.org/stable/c/db0250470f023f159094052c0bd5ab026a88ae93
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52915.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52915
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
