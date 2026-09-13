# [H] media: vidtv: initialize local pointers upon transfer of memory ownership

## Summary
Severity: High
Advisory: CVE-2025-68808
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2025-68808
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.248, >=5.11.0 <5.15.198, >=5.16.0 <6.1.160, >=6.2.0 <6.6.120, >=6.7.0 <6.12.64, >=6.13.0 <6.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: vidtv: initialize local pointers upon transfer of memory ownership

vidtv_channel_si_init() creates a temporary list (program, service, event)
and ownership of the memory itself is transferred to the PAT/SDT/EIT
tables through vidtv_psi_pat_program_assign(),
vidtv_psi_sdt_service_assign(), vidtv_psi_eit_event_assign().

The problem here is that the local pointer where the memory ownership
transfer was completed is not initialized to NULL. This causes the
vidtv_psi_pmt_create_sec_for_each_pat_entry() function to fail, and
in the flow that jumps to free_eit, the memory that was freed by
vidtv_psi_*_table_destroy() can be accessed again by
vidtv_psi_*_event_destroy() due to the uninitialized local pointer, so it
is freed once again.

Therefore, to prevent use-after-free and double-free vulnerability,
local pointers must be initialized to NULL when transferring memory
ownership.

## References
- https://git.kernel.org/stable/c/12ab6ebb37789b84073e83e4d9b14a5e0d133323
- https://git.kernel.org/stable/c/30f4d4e5224a9e44e9ceb3956489462319d804ce
- https://git.kernel.org/stable/c/3caa18d35f1dabe85a3dd31bc387f391ac9f9b4e
- https://git.kernel.org/stable/c/98aabfe2d79f74613abc2b0b1cef08f97eaf5322
- https://git.kernel.org/stable/c/a69c7fd603bf5ad93177394fbd9711922ee81032
- https://git.kernel.org/stable/c/c342e294dac4988c8ada759b2f057246e48c5108
- https://git.kernel.org/stable/c/fb9bd6d8d314b748e946ed6555eb4a956ee8c4d8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68808.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68808
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
