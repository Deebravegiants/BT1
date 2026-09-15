# [H] drm/edid: fix OOB read in drm_parse_tiled_block()

## Summary
Severity: High
Advisory: CVE-2026-64546
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-27
Source: https://osv.dev/vulnerability/CVE-2026-64546
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.19.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/edid: fix OOB read in drm_parse_tiled_block()

drm_parse_tiled_block() casts the DisplayID block to a
struct displayid_tiled_block and reads the full fixed layout up to
tile->topology_id[7] without checking block->num_bytes. The DisplayID
iterator only validates the declared payload length, so a crafted EDID
can advertise a tiled-display block (tag DATA_BLOCK_TILED_DISPLAY, or
DATA_BLOCK_2_TILED_DISPLAY_TOPOLOGY for v2.0) with a small num_bytes at
the end of a DisplayID extension. The read then runs past the end of the
exact-sized kmemdup()'d EDID allocation, a heap out-of-bounds read.

Reject blocks shorter than the spec's 22-byte tiled payload before
reading the fixed struct, as drm_parse_vesa_mso_data() already does.

  BUG: KASAN: slab-out-of-bounds in drm_edid_connector_update
  Read of size 2 at addr ffff888010077700 by task exploit/147
   dump_stack_lvl (lib/dump_stack.c:94 ...)
   print_report (mm/kasan/report.c:378 ...)
   kasan_report (mm/kasan/report.c:595)
   drm_edid_connector_update (drivers/gpu/drm/drm_edid.c:7581)
   bochs_connector_helper_get_modes (drivers/gpu/drm/tiny/bochs.c:574)
   drm_helper_probe_single_connector_modes (drivers/gpu/drm/drm_probe_helper.c:426)
   status_store (drivers/gpu/drm/drm_sysfs.c:219)
   ...
   vfs_write (fs/read_write.c:595 fs/read_write.c:688)
   ksys_write (fs/read_write.c:740)

## References
- https://git.kernel.org/stable/c/157727131ce8a52d8d9bc676c372ef82db6436c4
- https://git.kernel.org/stable/c/4137e1ecec9c8cb6c4fcee28ffabbbc7409eb7fb
- https://git.kernel.org/stable/c/4f5484d25f85ad6c989bad5f6a43450cecfcfd28
- https://git.kernel.org/stable/c/9acd5c1ddc17ca4c5ffa0c373e3fdf480506e061
- https://git.kernel.org/stable/c/9cc0f8e63e8c34cf43def35cbd305ba711181a1f
- https://git.kernel.org/stable/c/bfa05d89dc3ca3fb1a9099ef5185549a5ec8490d
- https://git.kernel.org/stable/c/c4ab04ca1bbf87eefa9fec5c80e1880450d2e7c0
- https://git.kernel.org/stable/c/faaa1e1155833e7d4ce7e3cfaf64c0d636b190db
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64546.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64546
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
