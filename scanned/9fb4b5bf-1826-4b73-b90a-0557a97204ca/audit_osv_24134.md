# [H] block, bfq: fix uaf for bfqq in bfq_exit_icq_bfqq

## Summary
Severity: High
Advisory: CVE-2022-50329
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2022-50329
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.86 <5.15.87, >=6.0.16 <6.0.17, >=6.1.2 <6.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

block, bfq: fix uaf for bfqq in bfq_exit_icq_bfqq

Commit 64dc8c732f5c ("block, bfq: fix possible uaf for 'bfqq->bic'")
will access 'bic->bfqq' in bic_set_bfqq(), however, bfq_exit_icq_bfqq()
can free bfqq first, and then call bic_set_bfqq(), which will cause uaf.

Fix the problem by moving bfq_exit_bfqq() behind bic_set_bfqq().

## References
- https://git.kernel.org/stable/c/1425f1bb5df5239021fd09ebc2a5e8070e705d36
- https://git.kernel.org/stable/c/1ed959fef5b1c6f1a7a3fbea543698c30ebd6678
- https://git.kernel.org/stable/c/246cf66e300b76099b5dbd3fdd39e9a5dbc53f02
- https://git.kernel.org/stable/c/7949b0df3dd9f4817ed4a4e989fa9ee81df6205f
- https://git.kernel.org/stable/c/cfe5b38c37720313eff0dec5517442c7ab3c9a20
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50329.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50329
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
