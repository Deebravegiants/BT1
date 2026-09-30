# [H] netfilter: nft_set_rbtree: skip end interval element from gc

## Summary
Severity: High
Advisory: CVE-2024-26581
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-20
Source: https://osv.dev/vulnerability/CVE-2024-26581
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.269, >=5.5.0 <5.10.210, >=5.11.0 <5.15.149, >=5.16.0 <6.1.78, >=6.2.0 <6.6.17, >=6.5.0 <6.7.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nft_set_rbtree: skip end interval element from gc

rbtree lazy gc on insert might collect an end interval element that has
been just added in this transactions, skip end interval elements that
are not yet active.

## References
- https://git.kernel.org/stable/c/10e9cb39313627f2eae4cd70c4b742074e998fd8
- https://git.kernel.org/stable/c/1296c110c5a0b45a8fcf58e7d18bc5da61a565cb
- https://git.kernel.org/stable/c/2bab493a5624444ec6e648ad0d55a362bcb4c003
- https://git.kernel.org/stable/c/4cee42fcf54fec46b344681e7cc4f234bb22f85a
- https://git.kernel.org/stable/c/60c0c230c6f046da536d3df8b39a20b9a9fd6af0
- https://git.kernel.org/stable/c/6eb14441f10602fa1cf691da9d685718b68b78a9
- https://git.kernel.org/stable/c/b734f7a47aeb32a5ba298e4ccc16bb0c52b6dbf7
- https://git.kernel.org/stable/c/c60d252949caf9aba537525195edae6bbabc35eb
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26581.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26581
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
