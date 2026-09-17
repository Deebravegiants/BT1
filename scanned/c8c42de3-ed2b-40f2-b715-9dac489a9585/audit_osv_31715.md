# [H] zram: fix potential UAF of zram table

## Summary
Severity: High
Advisory: CVE-2025-21671
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-31
Source: https://osv.dev/vulnerability/CVE-2025-21671
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.122 <6.1.127, >=6.6.68 <6.6.74, >=6.12.7 <6.12.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

zram: fix potential UAF of zram table

If zram_meta_alloc failed early, it frees allocated zram->table without
setting it NULL.  Which will potentially cause zram_meta_free to access
the table if user reset an failed and uninitialized device.

## References
- https://git.kernel.org/stable/c/212fe1c0df4a150fb6298db2cfff267ceaba5402
- https://git.kernel.org/stable/c/571d3f6045cd3a6d9f6aec33b678f3ffe97582ef
- https://git.kernel.org/stable/c/902ef8f16d5ca77edc77c30656be54186c1e99b7
- https://git.kernel.org/stable/c/fe3de867f94819ba0f28e035c0b0182150147d95
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21671.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21671
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
