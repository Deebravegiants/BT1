# [H] RDMA/bnxt_re: Fix a bug while setting up Level-2 PBL pages

## Summary
Severity: High
Advisory: CVE-2024-50208
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-08
Source: https://osv.dev/vulnerability/CVE-2024-50208
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.229, >=5.11.0 <5.15.170, >=5.16.0 <6.1.115, >=6.2.0 <6.6.59, >=6.7.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/bnxt_re: Fix a bug while setting up Level-2 PBL pages

Avoid memory corruption while setting up Level-2 PBL pages for the non MR
resources when num_pages > 256K.

There will be a single PDE page address (contiguous pages in the case of >
PAGE_SIZE), but, current logic assumes multiple pages, leading to invalid
memory access after 256K PBL entries in the PDE.

## References
- https://git.kernel.org/stable/c/7988bdbbb85ac85a847baf09879edcd0f70521dc
- https://git.kernel.org/stable/c/87cb3b0054e53e0155b630bdf8fb714ded62565f
- https://git.kernel.org/stable/c/daac56dd98e1ba814c878ac0acd482a37f2ab94b
- https://git.kernel.org/stable/c/de5857fa7bcc9a496a914c7e21390be873109f26
- https://git.kernel.org/stable/c/df6fed0a2a1a5e57f033bca40dc316b18e0d0ce6
- https://git.kernel.org/stable/c/ea701c1849e7250ea41a4f7493e0a5f136c1d47e
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50208.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50208
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
