# [C] netfilter: nf_conntrack_expect: use expect->helper

## Summary
Severity: Critical
Advisory: CVE-2026-31414
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-13
Source: https://osv.dev/vulnerability/CVE-2026-31414
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.30 <6.1.168, >=6.2.0 <6.6.134, >=6.7.0 <6.12.81, >=6.13.0 <6.18.22, >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_conntrack_expect: use expect->helper

Use expect->helper in ctnetlink and /proc to dump the helper name.
Using nfct_help() without holding a reference to the master conntrack
is unsafe.

Use exp->master->helper in ctnetlink path if userspace does not provide
an explicit helper when creating an expectation to retain the existing
behaviour. The ctnetlink expectation path holds the reference on the
master conntrack and nf_conntrack_expect lock and the nfnetlink glue
path refers to the master ct that is attached to the skb.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/3dfd3f7712b5a800f2ba632179e9b738076a51f0
- https://git.kernel.org/stable/c/4bd1b3d839172724b33d8d02c5a4ff6a1c775417
- https://git.kernel.org/stable/c/847cb7fe26c5ce5dce0d1a41fac1ea488b7f1781
- https://git.kernel.org/stable/c/b53294bff19e56ada2f230ceb8b1ffde61cc3817
- https://git.kernel.org/stable/c/e7ccaa0a62a8ff2be5d521299ce79390c318d306
- https://git.kernel.org/stable/c/f01794106042ee27e54af6fdf5b319a2fe3df94d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31414.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31414
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
