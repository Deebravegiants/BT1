# [M] block: ublk: make sure that block size is set correctly

## Summary
Severity: Medium
Advisory: CVE-2023-53269
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53269
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.24, >=6.2.0 <6.2.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

block: ublk: make sure that block size is set correctly

block size is one very key setting for block layer, and bad block size
could panic kernel easily.

Make sure that block size is set correctly.

Meantime if ublk_validate_params() fails, clear ub->params so that disk
is prevented from being added.

## References
- https://git.kernel.org/stable/c/1d1665279a845d16c93687389e364386e3fe0f38
- https://git.kernel.org/stable/c/231a49460ac0203270da2471928d392e5586370f
- https://git.kernel.org/stable/c/9dbe85ac618ef6ae60abe5dd17ae2b29065d9c1e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53269.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53269
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
