# [H] net: devmem: prevent net-iov / page mixing

## Summary
Severity: High
Advisory: CVE-2026-74627
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74627
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: devmem: prevent net-iov / page mixing

We should either have net_iov or page backed frags in a single skb,
otherwise it blows up down the stack. Don't allow mixing in
zerocopy_fill_skb_from_devmem().

## References
- https://git.kernel.org/stable/c/53a43508ee332d8bffe40590c3d189c92a551f9f
- https://git.kernel.org/stable/c/e9bfe12b1d04c34c6fedcba21d9709b65c08aa33
- https://git.kernel.org/stable/c/ed08011ae0be88f16cceae190535d6c790c83b0c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74627.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74627
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
