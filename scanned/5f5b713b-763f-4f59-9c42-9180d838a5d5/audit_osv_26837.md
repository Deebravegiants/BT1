# [H] erofs: stop parsing non-compact HEAD index if clusterofs is invalid

## Summary
Severity: High
Advisory: CVE-2023-54132
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2023-54132
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <5.4.243, >=5.5.0 <5.10.180, >=5.11.0 <5.15.111, >=5.16.0 <6.1.28, >=6.2.0 <6.2.15, >=6.3.0 <6.3.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

erofs: stop parsing non-compact HEAD index if clusterofs is invalid

Syzbot generated a crafted image [1] with a non-compact HEAD index of
clusterofs 33024 while valid numbers should be 0 ~ lclustersize-1,
which causes the following unexpected behavior as below:

 BUG: unable to handle page fault for address: fffff52101a3fff9
 #PF: supervisor read access in kernel mode
 #PF: error_code(0x0000) - not-present page
 PGD 23ffed067 P4D 23ffed067 PUD 0
 Oops: 0000 [#1] PREEMPT SMP KASAN
 CPU: 1 PID: 4398 Comm: kworker/u5:1 Not tainted 6.3.0-rc6-syzkaller-g09a9639e56c0 #0
 Hardware name: Google Google Compute Engine/Google Compute Engine, BIOS Google 03/30/2023
 Workqueue: erofs_worker z_erofs_decompressqueue_work
 RIP: 0010:z_erofs_decompress_queue+0xb7e/0x2b40
 ...
 Call Trace:
  <TASK>
  z_erofs_decompressqueue_work+0x99/0xe0
  process_one_work+0x8f6/0x1170
  worker_thread+0xa63/0x1210
  kthread+0x270/0x300
  ret_from_fork+0x1f/0x30

Note that normal images or images using compact indexes are not
impacted.  Let's fix this now.

[1] https://lore.kernel.org/r/000000000000ec75b005ee97fbaa@google.com

## References
- https://git.kernel.org/stable/c/060fecf1114ff9fcfe87953fe8c4fc5048777160
- https://git.kernel.org/stable/c/7a4579cd6e4936de107c82499c3c9ee11b63401e
- https://git.kernel.org/stable/c/7ee7a86e28ce9ead7112286c388df8d254c373c6
- https://git.kernel.org/stable/c/880c79bdb002b9d5b6940e52c2ad3829c2178207
- https://git.kernel.org/stable/c/96a845419b3722869f09883319de4d55c44d9aef
- https://git.kernel.org/stable/c/cc4efd3dd2ac9f89143e5d881609747ecff04164
- https://git.kernel.org/stable/c/f01b2894928affa3339d355608713cf3db8360b8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54132.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54132
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
