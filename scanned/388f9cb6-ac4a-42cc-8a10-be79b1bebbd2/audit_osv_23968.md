# [M] cpufreq: CPPC: Add u64 casts to avoid overflowing

## Summary
Severity: Medium
Advisory: CVE-2022-49750
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2022-49750
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

cpufreq: CPPC: Add u64 casts to avoid overflowing

The fields of the _CPC object are unsigned 32-bits values.
To avoid overflows while using _CPC's values, add 'u64' casts.

## References
- https://git.kernel.org/stable/c/7d596bbc66a52ff2c7a83d7e0ee840cb07e2a045
- https://git.kernel.org/stable/c/f5f94b9c8b805d87ff185caf9779c3a4d07819e3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49750.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49750
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
