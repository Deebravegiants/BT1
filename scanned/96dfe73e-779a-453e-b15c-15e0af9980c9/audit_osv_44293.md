# [H] regulator: fp9931: Fix VPOS/VNEG voltage selector table

## Summary
Severity: High
Advisory: CVE-2026-80745
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-80745
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

regulator: fp9931: Fix VPOS/VNEG voltage selector table

The VPOSNEG_table[] mapping does not match the FP9931 datasheet.

The datasheet defines the VPOS/VNEG voltage mapping as:

  00h-04h ->  7.04V (-7.04V)
  05h     ->  7.26V (-7.26V)
  06h     ->  7.49V (-7.49V)
  ...
  28h-3Fh -> 15.06V (-15.06V)

However, VPOSNEG_table[] has two issues:

1. Selector 0x00~0x04 should all map to 7.04V (5 entries), but the
   table has 6 entries of 7.04V, causing all subsequent entries to be
   shifted by one position.

2. Selectors 0x29~0x3F should all clamp to 15.06V (23 entries), but
   the table has only 41 entries. Any selector value above 0x28
   would result in an out-of-bounds table access.

Fix both issues by removing the duplicate 7.04V entry and appending
the missing 23 clamped 15.06V entries, bringing the table to the
correct size of 64 entries (0x00~0x3F).

## References
- https://git.kernel.org/stable/c/66694b5f90f3876fccb87bbd02b453cdc33b3ae4
- https://git.kernel.org/stable/c/92a9594053831bf4c5886519688e155912befaee
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80745.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80745
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
