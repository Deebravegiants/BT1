# [H] io_uring/kbuf: check if target buffer list is still legacy on recycle

## Summary
Severity: High
Advisory: CVE-2026-43366
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43366
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.19, >=6.19.0 <6.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

io_uring/kbuf: check if target buffer list is still legacy on recycle

There's a gap between when the buffer was grabbed and when it
potentially gets recycled, where if the list is empty, someone could've
upgraded it to a ring provided type. This can happen if the request
is forced via io-wq. The legacy recycling is missing checking if the
buffer_list still exists, and if it's of the correct type. Add those
checks.

## References
- https://git.kernel.org/stable/c/439a6728ec4641ffad1ca796622c19bc525e570f
- https://git.kernel.org/stable/c/50ad880db3013c6fee0ef13781762a39e2e7ef83
- https://git.kernel.org/stable/c/97b57f69fee1b61b41acbf37e7720cac9d389fa4
- https://git.kernel.org/stable/c/a7b33671e418fca507feebd1d56e7f4952a4b25c
- https://git.kernel.org/stable/c/c2c185be5c85d37215397c8e8781abf0a69bec1f
- https://git.kernel.org/stable/c/f3fb54e7a8b4aadcc2836ee463eec8c88709b8aa
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43366.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43366
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
