# [H] batman-adv: bla: reacquire gw address after skb realloc

## Summary
Severity: High
Advisory: CVE-2026-72233
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72233
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

batman-adv: bla: reacquire gw address after skb realloc

The pskb_may_pull() called by batadv_bla_is_backbone_gw() could reallocate
the buffer behind the skb. Variables which were pointing to the old buffer
need to be reassigned to avoid an use-after-free.

## References
- https://git.kernel.org/stable/c/41819c5467b6eb8ab4567f0ac98702ce9b6abbb1
- https://git.kernel.org/stable/c/4a6673c55752a7aa41e28f51660eb981504ca088
- https://git.kernel.org/stable/c/a9ab19fbca86b32e9a9ae9e1a63e70a7eab3400f
- https://git.kernel.org/stable/c/ab2bac47a02637df1128a151e81d3ec14767f4bb
- https://git.kernel.org/stable/c/cdf3b5af2bc4431e58629e8ad2086b1e9185c761
- https://git.kernel.org/stable/c/dc16bbf53cede1baf564bf0c8a861114b64e18b3
- https://git.kernel.org/stable/c/e5e18886aadd3870e2d84e32a9678317fab1dd9e
- https://git.kernel.org/stable/c/f4fb97ecf677cd9c3aa4f3bfc6fbf5b0e4bdbbbf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72233.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72233
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
