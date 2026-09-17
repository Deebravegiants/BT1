# [H] net: txgbe: fix heap overflow when reading module EEPROM

## Summary
Severity: High
Advisory: CVE-2026-68440
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-68440
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: txgbe: fix heap overflow when reading module EEPROM

txgbe_read_eeprom_hostif() always copies round_up(length, 4) bytes
into the caller buffer, which ethtool allocates with exactly 'length'
bytes. A non-4-aligned length therefore causes an out-of-bounds write.
Copy only the remaining bytes on the final dword instead.

## References
- https://git.kernel.org/stable/c/6a905a71fd43ce8b45f05044b11491337f232c9d
- https://git.kernel.org/stable/c/febcced6958158e7e90a55a8567b3f5c3639c0b9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68440.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68440
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
