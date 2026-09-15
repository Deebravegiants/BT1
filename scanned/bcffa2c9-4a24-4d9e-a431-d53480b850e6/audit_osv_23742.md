# [C] NFSv4: Fix free of uninitialized nfs4_label on referral lookup.

## Summary
Severity: Critical
Advisory: CVE-2022-49418
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49418
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFSv4: Fix free of uninitialized nfs4_label on referral lookup.

Send along the already-allocated fattr along with nfs4_fs_locations, and
drop the memcpy of fattr.  We end up growing two more allocations, but this
fixes up a crash as:

PID: 790    TASK: ffff88811b43c000  CPU: 0   COMMAND: "ls"
 #0 [ffffc90000857920] panic at ffffffff81b9bfde
 #1 [ffffc900008579c0] do_trap at ffffffff81023a9b
 #2 [ffffc90000857a10] do_error_trap at ffffffff81023b78
 #3 [ffffc90000857a58] exc_stack_segment at ffffffff81be1f45
 #4 [ffffc90000857a80] asm_exc_stack_segment at ffffffff81c009de
 #5 [ffffc90000857b08] nfs_lookup at ffffffffa0302322 [nfs]
 #6 [ffffc90000857b70] __lookup_slow at ffffffff813a4a5f
 #7 [ffffc90000857c60] walk_component at ffffffff813a86c4
 #8 [ffffc90000857cb8] path_lookupat at ffffffff813a9553
 #9 [ffffc90000857cf0] filename_lookup at ffffffff813ab86b

## References
- https://git.kernel.org/stable/c/6015292653d95ba9f72906e2b65e536aa5807d64
- https://git.kernel.org/stable/c/c3ed222745d9ad7b69299b349a64ba533c64a34f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49418.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49418
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
