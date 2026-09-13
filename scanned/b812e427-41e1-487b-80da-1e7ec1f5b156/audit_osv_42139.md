# [H] ksmbd: validate compound request size before reading StructureSize2

## Summary
Severity: High
Advisory: CVE-2026-64578
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-64578
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: validate compound request size before reading StructureSize2

When ksmbd validates a compound (chained) SMB2 request,
ksmbd_smb2_check_message() reads pdu->StructureSize2 without first
checking that the compound element is large enough to contain it.
StructureSize2 is a 2-byte field at offset 64
(__SMB2_HEADER_STRUCTURE_SIZE) from the start of each element.

The compound-walking logic only guarantees that a full 64-byte SMB2
header is present for the trailing element: when NextCommand is 0, len is
reduced to the number of bytes remaining after next_smb2_rcv_hdr_off. A
remote client can craft a compound request whose last element has exactly
64 bytes, so the 2-byte StructureSize2 read at offset 64 extends one byte
past the receive buffer, producing a slab-out-of-bounds read.

  BUG: KASAN: slab-out-of-bounds in ksmbd_smb2_check_message (fs/smb/server/smb2misc.c:402)
  Read of size 2 at addr ffff888012ae31ac by task kworker/0:1/14
  The buggy address is located 172 bytes inside of allocated 173-byte region
  Workqueue: ksmbd-io handle_ksmbd_work
  Call Trace:
   ...
   kasan_report (mm/kasan/report.c:595)
   ksmbd_smb2_check_message (fs/smb/server/smb2misc.c:402)
   handle_ksmbd_work (fs/smb/server/server.c:119)
   process_one_work (kernel/workqueue.c:3314)
   worker_thread (kernel/workqueue.c:3397)
   kthread (kernel/kthread.c:436)
   ret_from_fork (arch/x86/kernel/process.c:158)
   ret_from_fork_asm (arch/x86/entry/entry_64.S:245)

Reject any compound element that is too small to hold StructureSize2
before dereferencing it.

## References
- https://git.kernel.org/stable/c/15b38176fd1530372905c602fde51fe89ec8c877
- https://git.kernel.org/stable/c/1b6740525f5af90868d557c31b496ae689c8c549
- https://git.kernel.org/stable/c/2c307126ed8e7adddab82b8e31d962d3a2156ab1
- https://git.kernel.org/stable/c/415d0fff0451ad7ad4caa910f2bb0f562f0fd60f
- https://git.kernel.org/stable/c/ea128f06d2fb2186f0cac0c9f3e953e4d1f5c29a
- https://git.kernel.org/stable/c/f0e337e7db67cc1c832958bbb6c4026bdceacfdb
- https://git.kernel.org/stable/c/f7550a91ab211726f59cb137523b7a9eae1ac6eb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64578.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64578
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
