# [H] octeontx2-pf: Fix SQE threshold checking

## Summary
Severity: High
Advisory: CVE-2022-49858
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49858
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <6.0.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

octeontx2-pf: Fix SQE threshold checking

Current way of checking available SQE count which is based on
HW updated SQB count could result in driver submitting an SQE
even before CQE for the previously transmitted SQE at the same
index is processed in NAPI resulting losing SKB pointers,
hence a leak. Fix this by checking a consumer index which
is updated once CQE is processed.

## References
- https://git.kernel.org/stable/c/015e3c0a3b16193aab23beefe4719484b9984c2d
- https://git.kernel.org/stable/c/f0dfc4c88ef39be0ba736aa0ce6119263fc19aeb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49858.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49858
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
