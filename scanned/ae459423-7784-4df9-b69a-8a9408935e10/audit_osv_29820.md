# [H] ethtool: fail closed if we can't get max channel used in indirection tables

## Summary
Severity: High
Advisory: CVE-2024-46834
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-27
Source: https://osv.dev/vulnerability/CVE-2024-46834
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.6.0 <6.10.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

ethtool: fail closed if we can't get max channel used in indirection tables

Commit 0d1b7d6c9274 ("bnxt: fix crashes when reducing ring count with
active RSS contexts") proves that allowing indirection table to contain
channels with out of bounds IDs may lead to crashes. Currently the
max channel check in the core gets skipped if driver can't fetch
the indirection table or when we can't allocate memory.

Both of those conditions should be extremely rare but if they do
happen we should try to be safe and fail the channel change.

## References
- https://git.kernel.org/stable/c/101737d8b88dbd4be6010bac398fe810f1950036
- https://git.kernel.org/stable/c/2899d58462ba868287d6ff3acad3675e7adf934f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46834.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46834
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
