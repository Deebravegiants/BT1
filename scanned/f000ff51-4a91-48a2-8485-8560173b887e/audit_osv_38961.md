# [C] netconsole: avoid OOB reads, msg is not nul-terminated

## Summary
Severity: Critical
Advisory: CVE-2026-43197
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43197
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.12.103, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

netconsole: avoid OOB reads, msg is not nul-terminated

msg passed to netconsole from the console subsystem is not guaranteed
to be nul-terminated. Before recent
commit 7eab73b18630 ("netconsole: convert to NBCON console infrastructure")
the message would be placed in printk_shared_pbufs, a static global
buffer, so KASAN had harder time catching OOB accesses. Now we see:

    printk: console [netcon_ext0] enabled
    BUG: KASAN: slab-out-of-bounds in string+0x1f7/0x240
    Read of size 1 at addr ffff88813b6d4c00 by task pr/netcon_ext0/594

    CPU: 65 UID: 0 PID: 594 Comm: pr/netcon_ext0 Not tainted 6.19.0-11754-g4246fd6547c9
    Call Trace:
     kasan_report+0xe4/0x120
     string+0x1f7/0x240
     vsnprintf+0x655/0xba0
     scnprintf+0xba/0x120
     netconsole_write+0x3fe/0xa10
     nbcon_emit_next_record+0x46e/0x860
     nbcon_kthread_func+0x623/0x750

    Allocated by task 1:
     nbcon_alloc+0x1ea/0x450
     register_console+0x26b/0xe10
     init_netconsole+0xbb0/0xda0

    The buggy address belongs to the object at ffff88813b6d4000
                which belongs to the cache kmalloc-4k of size 4096
    The buggy address is located 0 bytes to the right of
                allocated 3072-byte region [ffff88813b6d4000, ffff88813b6d4c00)

## References
- https://git.kernel.org/stable/c/3126a2f98beaec5a554a1fb31c46db1e8542665e
- https://git.kernel.org/stable/c/74ab1456eaa3b2eb986138f9e1f4cb37e73b6f58
- https://git.kernel.org/stable/c/82aec772fca2223bc5774bd9af486fd95766e578
- https://git.kernel.org/stable/c/8fe132c4873f9eb1b86ddbf31216e9d961a0b8b9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43197.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43197
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
