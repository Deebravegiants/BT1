# [H] x86/CPU/AMD: Add missing terminator for zen5_rdseed_microcode

## Summary
Severity: High
Advisory: CVE-2025-68195
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-68195
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

x86/CPU/AMD: Add missing terminator for zen5_rdseed_microcode

Running x86_match_min_microcode_rev() on a Zen5 CPU trips up KASAN for an out
of bounds access.

## References
- https://git.kernel.org/stable/c/4c6b56a76478bd1ab609827c571905386c11d308
- https://git.kernel.org/stable/c/f1fdffe0afea02ba783acfe815b6a60e7180df40
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68195.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68195
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
