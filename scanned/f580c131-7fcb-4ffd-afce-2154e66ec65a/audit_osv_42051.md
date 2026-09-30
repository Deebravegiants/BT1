# [H] coresight: ultrasoc-smb: Fix OOB write in smb_sync_perf_buffer()

## Summary
Severity: High
Advisory: CVE-2026-64402
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64402
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

coresight: ultrasoc-smb: Fix OOB write in smb_sync_perf_buffer()

When the SMB sink is used as a perf AUX sink, smb_update_buffer() calls
smb_sync_perf_buffer() to copy hardware trace data into the perf AUX ring
buffer pages. It derives pg_idx = head >> PAGE_SHIFT from @head, which is
handle->head, and indexes dst_pages[pg_idx]. The pg_idx %= nr_pages
normalization is only applied after the first loop iteration.

This leaves the initial page index underived from the buffer size, which
can result in an out-of-bounds write past dst_pages[] when head exceeds
the AUX buffer size.

Normalize head modulo the AUX buffer size before deriving the page index
and offset, mirroring tmc_etr_sync_perf_buffer().

## References
- https://git.kernel.org/stable/c/38dbc8db8341ccdf8e1e1a067453d33ad751864b
- https://git.kernel.org/stable/c/4c5a0a946373da99a80398289b28845b5ae40cd1
- https://git.kernel.org/stable/c/661a019ac0413ecec9e5d1dfcc12fbca8e78d5fb
- https://git.kernel.org/stable/c/98495b5a4d77dd22e106f462b76e1093a55b29a7
- https://git.kernel.org/stable/c/daf6246ab988fc8bdc82ad7c8d0b1c182d11b15f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64402.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64402
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
