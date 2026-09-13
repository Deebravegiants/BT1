# [H] vt: discard stale unicode buffer on alt screen exit after resize

## Summary
Severity: High
Advisory: CVE-2026-31742
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-31742
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.20 <6.18.22, >=6.19.10 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

vt: discard stale unicode buffer on alt screen exit after resize

When enter_alt_screen() saves vc_uni_lines into vc_saved_uni_lines and
sets vc_uni_lines to NULL, a subsequent console resize via vc_do_resize()
skips reallocating the unicode buffer because vc_uni_lines is NULL.
However, vc_saved_uni_lines still points to the old buffer allocated for
the original dimensions.

When leave_alt_screen() later restores vc_saved_uni_lines, the buffer
dimensions no longer match vc_rows/vc_cols. Any operation that iterates
over the unicode buffer using the current dimensions (e.g. csi_J clearing
the screen) will access memory out of bounds, causing a kernel oops:

  BUG: unable to handle page fault for address: 0x0000002000000020
  RIP: 0010:csi_J+0x133/0x2d0

The faulting address 0x0000002000000020 is two adjacent u32 space
characters (0x20) interpreted as a pointer, read from the row data area
past the end of the 25-entry pointer array in a buffer allocated for
80x25 but accessed with 240x67 dimensions.

Fix this by checking whether the console dimensions changed while in the
alternate screen. If they did, free the stale saved buffer instead of
restoring it. The unicode screen will be lazily rebuilt via
vc_uniscr_check() when next needed.

## References
- https://git.kernel.org/stable/c/40014493cece72a0be5672cd86763e53fb3ec613
- https://git.kernel.org/stable/c/428fdf55301e6c8fa5a36b426240797b1cf86570
- https://git.kernel.org/stable/c/891d790fdb5c96c6e1d2841e06ee6c360f2d1288
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31742.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31742
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
