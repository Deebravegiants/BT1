# [H] drm/xe: always keep track of remap prev/next

## Summary
Severity: High
Advisory: CVE-2026-31479
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-31479
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.80, >=6.13.0 <6.18.21, >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe: always keep track of remap prev/next

During 3D workload, user is reporting hitting:

[  413.361679] WARNING: drivers/gpu/drm/xe/xe_vm.c:1217 at vm_bind_ioctl_ops_unwind+0x1e2/0x2e0 [xe], CPU#7: vkd3d_queue/9925
[  413.361944] CPU: 7 UID: 1000 PID: 9925 Comm: vkd3d_queue Kdump: loaded Not tainted 7.0.0-070000rc3-generic #202603090038 PREEMPT(lazy)
[  413.361949] RIP: 0010:vm_bind_ioctl_ops_unwind+0x1e2/0x2e0 [xe]
[  413.362074] RSP: 0018:ffffd4c25c3df930 EFLAGS: 00010282
[  413.362077] RAX: 0000000000000000 RBX: ffff8f3ee817ed10 RCX: 0000000000000000
[  413.362078] RDX: 0000000000000000 RSI: 0000000000000000 RDI: 0000000000000000
[  413.362079] RBP: ffffd4c25c3df980 R08: 0000000000000000 R09: 0000000000000000
[  413.362081] R10: 0000000000000000 R11: 0000000000000000 R12: ffff8f41fbf99380
[  413.362082] R13: ffff8f3ee817e968 R14: 00000000ffffffef R15: ffff8f43d00bd380
[  413.362083] FS:  00000001040ff6c0(0000) GS:ffff8f4696d89000(0000) knlGS:00000000330b0000
[  413.362085] CS:  0010 DS: 002b ES: 002b CR0: 0000000080050033
[  413.362086] CR2: 00007ddfc4747000 CR3: 00000002e6262005 CR4: 0000000000f72ef0
[  413.362088] PKRU: 55555554
[  413.362089] Call Trace:
[  413.362092]  <TASK>
[  413.362096]  xe_vm_bind_ioctl+0xa9a/0xc60 [xe]

Which seems to hint that the vma we are re-inserting for the ops unwind
is either invalid or overlapping with something already inserted in the
vm. It shouldn't be invalid since this is a re-insertion, so must have
worked before. Leaving the likely culprit as something already placed
where we want to insert the vma.

Following from that, for the case where we do something like a rebind in
the middle of a vma, and one or both mapped ends are already compatible,
we skip doing the rebind of those vma and set next/prev to NULL. As well
as then adjust the original unmap va range, to avoid unmapping the ends.
However, if we trigger the unwind path, we end up with three va, with
the two ends never being removed and the original va range in the middle
still being the shrunken size.

If this occurs, one failure mode is when another unwind op needs to
interact with that range, which can happen with a vector of binds. For
example, if we need to re-insert something in place of the original va.
In this case the va is still the shrunken version, so when removing it
and then doing a re-insert it can overlap with the ends, which were
never removed, triggering a warning like above, plus leaving the vm in a
bad state.

With that, we need two things here:

 1) Stop nuking the prev/next tracking for the skip cases. Instead
    relying on checking for skip prev/next, where needed. That way on the
    unwind path, we now correctly remove both ends.

 2) Undo the unmap va shrinkage, on the unwind path. With the two ends
    now removed the unmap va should expand back to the original size again,
    before re-insertion.

v2:
  - Update the explanation in the commit message, based on an actual IGT of
    triggering this issue, rather than conjecture.
  - Also undo the unmap shrinkage, for the skip case. With the two ends
    now removed, the original unmap va range should expand back to the
    original range.
v3:
  - Track the old start/range separately. vma_size/start() uses the va
    info directly.

(cherry picked from commit aec6969f75afbf4e01fd5fb5850ed3e9c27043ac)

## References
- https://git.kernel.org/stable/c/5eda8001ebb5269755608d678dd1f3928ab077c9
- https://git.kernel.org/stable/c/bfe9e314d7574d1c5c851972e7aee342733819d2
- https://git.kernel.org/stable/c/ccd41f110c608b3cc347b9be881c3e72cd634b2b
- https://git.kernel.org/stable/c/e6ba1749549e87b83c0c4885d84b543687c3740e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31479.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31479
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
