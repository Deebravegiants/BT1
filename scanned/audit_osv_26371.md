# [H] block, bfq: fix uaf for bfqq in bic_set_bfqq()

## Summary
Severity: High
Advisory: CVE-2023-52983
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2023-52983
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.86 <5.15.93, >=6.1.2 <6.1.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

block, bfq: fix uaf for bfqq in bic_set_bfqq()

After commit 64dc8c732f5c ("block, bfq: fix possible uaf for 'bfqq->bic'"),
bic->bfqq will be accessed in bic_set_bfqq(), however, in some context
bic->bfqq will be freed, and bic_set_bfqq() is called with the freed
bic->bfqq.

Fix the problem by always freeing bfqq after bic_set_bfqq().

## References
- https://git.kernel.org/stable/c/511c922c5bf6c8a166bea826e702336bc2424140
- https://git.kernel.org/stable/c/7f77f3dab5066a7c9da73d72d1eee895ff84a8d5
- https://git.kernel.org/stable/c/b600de2d7d3a16f9007fad1bdae82a3951a26af2
- https://git.kernel.org/stable/c/cb1876fc33af26d00efdd473311f1b664c77c44e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52983.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52983
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
