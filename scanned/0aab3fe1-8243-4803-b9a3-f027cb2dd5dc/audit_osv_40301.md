# [H] ipc: limit next_id allocation to the valid ID range

## Summary
Severity: High
Advisory: CVE-2026-52923
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52923
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.8.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipc: limit next_id allocation to the valid ID range

The checkpoint/restore sysctl path can request the next SysV IPC id
through ids->next_id.  ipc_idr_alloc() currently forwards that request to
idr_alloc() with an open-ended upper bound.

If the valid tail of the SysV IPC id space is full, the allocation can
spill beyond ipc_mni.  The returned SysV IPC id still uses the normal
index encoding, so later lookup and removal can target the wrong slot. 
This leaves the real IDR entry behind and breaks the IDR state for the
object.

The bug is in ipc_idr_alloc() in the checkpoint/restore path.

1. ids->next_id is passed to:

       idr_alloc(&ids->ipcs_idr, new, ipcid_to_idx(next_id), 0, ...)

2. The zero upper bound makes the allocation effectively open-ended.
   Once the valid SysV IPC tail is occupied, idr_alloc() can spill past
   ipc_mni and allocate an entry beyond the valid IPC id range.

3. The new object id is still encoded with the narrower SysV IPC index
   width:

       new->id = (new->seq << ipcmni_seq_shift()) + idx

4. Later removal goes through ipc_rmid(), which uses:

       ipcid_to_idx(ipcp->id)

   That truncates the real IDR index. An object actually stored at a
   high index can then be removed as if it lived at a low in-range
   index.

5. For shared memory, shm_destroy() frees the current object anyway, but
   the real high IDR slot is left behind as a dangling pointer.

6. A subsequent walk of /proc/sysvipc/shm reaches the stale IDR entry
   and dereferences freed memory.

Prevent this by bounding the requested allocation to ipc_mni so the
checkpoint/restore path fails once the valid range is exhausted.

## References
- https://git.kernel.org/stable/c/157ce2c6836ce0ff19108a819f38df061345425f
- https://git.kernel.org/stable/c/3bbe2bb9111ce6967a951bfac79af142d816fae5
- https://git.kernel.org/stable/c/41058d4c3f63ab64901560a704882e0565f4e456
- https://git.kernel.org/stable/c/8c58a92849175f5e2ab7bc2734b3b89afe79f6ef
- https://git.kernel.org/stable/c/a3cc795129e5ec0f8948653a3bf471e7d8852f5e
- https://git.kernel.org/stable/c/af24e202b543ded8a34f1d5d3db54eb916173f04
- https://git.kernel.org/stable/c/bd4be70669af55b974860d13680348cfdf50bbed
- https://git.kernel.org/stable/c/fa0b9b2b7ae3539908d69c2b9ac0d144d9bc5139
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-52923.json
- https://access.redhat.com/errata/RHSA-2026:47248
- https://access.redhat.com/errata/RHSA-2026:48386
- https://access.redhat.com/errata/RHSA-2026:49031
- https://access.redhat.com/errata/RHSA-2026:49212
- https://access.redhat.com/errata/RHSA-2026:49851
- https://access.redhat.com/errata/RHSA-2026:49857
- https://access.redhat.com/errata/RHSA-2026:51603
- https://access.redhat.com/errata/RHSA-2026:51604
- https://access.redhat.com/errata/RHSA-2026:52649
- https://access.redhat.com/errata/RHSA-2026:52764
- https://access.redhat.com/errata/RHSA-2026:53330
