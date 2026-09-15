# [H] wifi: ath12k: Fix buffer overflow in debugfs

## Summary
Severity: High
Advisory: CVE-2025-38317
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-10
Source: https://osv.dev/vulnerability/CVE-2025-38317
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.34, >=6.13.0 <6.15.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: ath12k: Fix buffer overflow in debugfs

If the user tries to write more than 32 bytes then it results in memory
corruption.  Fortunately, this is debugfs so it's limited to root users.

## References
- https://git.kernel.org/stable/c/0c57aa8ef94cffc5c2d68230e19329a03e71a94f
- https://git.kernel.org/stable/c/8c4a200d03574bfcbf54fdb7ba5968b58ad2e0b3
- https://git.kernel.org/stable/c/8c7a5031a6b0d42e640fbd2d5d05f61f74e32dce
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38317.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38317
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
