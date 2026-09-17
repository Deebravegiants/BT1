# [H] ring-buffer: Do not swap cpu_buffer during resize process

## Summary
Severity: High
Advisory: CVE-2023-53718
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-22
Source: https://osv.dev/vulnerability/CVE-2023-53718
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.5.0 <5.10.192, >=5.11.0 <5.15.128, >=5.16.0 <6.1.47, >=6.2.0 <6.4.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

ring-buffer: Do not swap cpu_buffer during resize process

When ring_buffer_swap_cpu was called during resize process,
the cpu buffer was swapped in the middle, resulting in incorrect state.
Continuing to run in the wrong state will result in oops.

This issue can be easily reproduced using the following two scripts:
/tmp # cat test1.sh
//#! /bin/sh
for i in `seq 0 100000`
do
         echo 2000 > /sys/kernel/debug/tracing/buffer_size_kb
         sleep 0.5
         echo 5000 > /sys/kernel/debug/tracing/buffer_size_kb
         sleep 0.5
done
/tmp # cat test2.sh
//#! /bin/sh
for i in `seq 0 100000`
do
        echo irqsoff > /sys/kernel/debug/tracing/current_tracer
        sleep 1
        echo nop > /sys/kernel/debug/tracing/current_tracer
        sleep 1
done
/tmp # ./test1.sh &
/tmp # ./test2.sh &

A typical oops log is as follows, sometimes with other different oops logs.

[  231.711293] WARNING: CPU: 0 PID: 9 at kernel/trace/ring_buffer.c:2026 rb_update_pages+0x378/0x3f8
[  231.713375] Modules linked in:
[  231.714735] CPU: 0 PID: 9 Comm: kworker/0:1 Tainted: G        W          6.5.0-rc1-00276-g20edcec23f92 #15
[  231.716750] Hardware name: linux,dummy-virt (DT)
[  231.718152] Workqueue: events update_pages_handler
[  231.719714] pstate: 60000005 (nZCv daif -PAN -UAO -TCO -DIT -SSBS BTYPE=--)
[  231.721171] pc : rb_update_pages+0x378/0x3f8
[  231.722212] lr : rb_update_pages+0x25c/0x3f8
[  231.723248] sp : ffff800082b9bd50
[  231.724169] x29: ffff800082b9bd50 x28: ffff8000825f7000 x27: 0000000000000000
[  231.726102] x26: 0000000000000001 x25: fffffffffffff010 x24: 0000000000000ff0
[  231.728122] x23: ffff0000c3a0b600 x22: ffff0000c3a0b5c0 x21: fffffffffffffe0a
[  231.730203] x20: ffff0000c3a0b600 x19: ffff0000c0102400 x18: 0000000000000000
[  231.732329] x17: 0000000000000000 x16: 0000000000000000 x15: 0000ffffe7aa8510
[  231.734212] x14: 0000000000000000 x13: 0000000000000000 x12: 0000000000000002
[  231.736291] x11: ffff8000826998a8 x10: ffff800082b9baf0 x9 : ffff800081137558
[  231.738195] x8 : fffffc00030e82c8 x7 : 0000000000000000 x6 : 0000000000000001
[  231.740192] x5 : ffff0000ffbafe00 x4 : 0000000000000000 x3 : 0000000000000000
[  231.742118] x2 : 00000000000006aa x1 : 0000000000000001 x0 : ffff0000c0007208
[  231.744196] Call trace:
[  231.744892]  rb_update_pages+0x378/0x3f8
[  231.745893]  update_pages_handler+0x1c/0x38
[  231.746893]  process_one_work+0x1f0/0x468
[  231.747852]  worker_thread+0x54/0x410
[  231.748737]  kthread+0x124/0x138
[  231.749549]  ret_from_fork+0x10/0x20
[  231.750434] ---[ end trace 0000000000000000 ]---
[  233.720486] Unable to handle kernel NULL pointer dereference at virtual address 0000000000000000
[  233.721696] Mem abort info:
[  233.721935]   ESR = 0x0000000096000004
[  233.722283]   EC = 0x25: DABT (current EL), IL = 32 bits
[  233.722596]   SET = 0, FnV = 0
[  233.722805]   EA = 0, S1PTW = 0
[  233.723026]   FSC = 0x04: level 0 translation fault
[  233.723458] Data abort info:
[  233.723734]   ISV = 0, ISS = 0x00000004, ISS2 = 0x00000000
[  233.724176]   CM = 0, WnR = 0, TnD = 0, TagAccess = 0
[  233.724589]   GCS = 0, Overlay = 0, DirtyBit = 0, Xs = 0
[  233.725075] user pgtable: 4k pages, 48-bit VAs, pgdp=0000000104943000
[  233.725592] [0000000000000000] pgd=0000000000000000, p4d=0000000000000000
[  233.726231] Internal error: Oops: 0000000096000004 [#1] PREEMPT SMP
[  233.726720] Modules linked in:
[  233.727007] CPU: 0 PID: 9 Comm: kworker/0:1 Tainted: G        W          6.5.0-rc1-00276-g20edcec23f92 #15
[  233.727777] Hardware name: linux,dummy-virt (DT)
[  233.728225] Workqueue: events update_pages_handler
[  233.728655] pstate: 200000c5 (nzCv daIF -PAN -UAO -TCO -DIT -SSBS BTYPE=--)
[  233.729054] pc : rb_update_pages+0x1a8/0x3f8
[  233.729334] lr : rb_update_pages+0x154/0x3f8
[  233.729592] sp : ffff800082b9bd50
[  233.729792] x29: ffff800082b9bd50 x28: ffff8000825f7000 x27: 00000000
---truncated---

## References
- https://git.kernel.org/stable/c/02e52d7daaa3f0f48819f198092cf4871065bbf7
- https://git.kernel.org/stable/c/128c06a34cfe55212632533a706b050d54552741
- https://git.kernel.org/stable/c/49b830d75f03d5dd41146d10e4d3e2a8211c4b94
- https://git.kernel.org/stable/c/66a3b2a121386702663065d5c9e5a33c03d3f4a2
- https://git.kernel.org/stable/c/8a96c0288d0737ad77882024974c075345c72011
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53718.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53718
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
