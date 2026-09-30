# [H] regulator: rtq2208: Fix uninitialized use of regulator_config

## Summary
Severity: High
Advisory: CVE-2024-50300
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-50300
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.61, >=6.7.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

regulator: rtq2208: Fix uninitialized use of regulator_config

Fix rtq2208 driver uninitialized use to cause kernel error.

## References
- https://git.kernel.org/stable/c/2feb023110843acce790e9089e72e9a9503d9fa5
- https://git.kernel.org/stable/c/64fbab934ae59be9caffc80a75450984b1e108e0
- https://git.kernel.org/stable/c/9b7c0405af667857b3ad24a7ef6723f5475a9e43
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50300.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50300
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
