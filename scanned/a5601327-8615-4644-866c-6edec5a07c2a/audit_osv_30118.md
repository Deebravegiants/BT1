# [M] blk-mq: setup queue ->tag_set before initializing hctx

## Summary
Severity: Medium
Advisory: CVE-2024-50081
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-10-29
Source: https://osv.dev/vulnerability/CVE-2024-50081
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.11.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

blk-mq: setup queue ->tag_set before initializing hctx

Commit 7b815817aa58 ("blk-mq: add helper for checking if one CPU is mapped to specified hctx")
needs to check queue mapping via tag set in hctx's cpuhp handler.

However, q->tag_set may not be setup yet when the cpuhp handler is
enabled, then kernel oops is triggered.

Fix the issue by setup queue tag_set before initializing hctx.

## References
- https://git.kernel.org/stable/c/25466e5b4bb11a8415ce8d0be89ab77135f7e444
- https://git.kernel.org/stable/c/73d964ce4bc8b4de88a7c2e40df494f0d5cd8950
- https://git.kernel.org/stable/c/c25c0c9035bb8b28c844dfddeda7b8bdbcfcae95
- https://git.kernel.org/stable/c/d28b256db525d9432bc3eb2c8d83f7d3f5e1cc87
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50081.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50081
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
