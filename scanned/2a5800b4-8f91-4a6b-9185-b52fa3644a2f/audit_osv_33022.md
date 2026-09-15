# [H] spi: cs42l43: Property entry should be a null-terminated array

## Summary
Severity: High
Advisory: CVE-2025-38573
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2025-08-19
Source: https://osv.dev/vulnerability/CVE-2025-38573
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.42, >=6.13.0 <6.15.10, >=6.16.0 <6.16.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

spi: cs42l43: Property entry should be a null-terminated array

The software node does not specify a count of property entries, so the
array must be null-terminated.

When unterminated, this can lead to a fault in the downstream cs35l56
amplifier driver, because the node parse walks off the end of the
array into unknown memory.

## References
- https://git.kernel.org/stable/c/139b5df757a0aa436f763b0038e0b73808d2f4b6
- https://git.kernel.org/stable/c/674328102baad76c7a06628efc01974ece5ae27f
- https://git.kernel.org/stable/c/9f0035ae38d2571f5ddedc829d74492013caa625
- https://git.kernel.org/stable/c/ffcfd071eec7973e58c4ffff7da4cb0e9ca7b667
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38573.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38573
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
