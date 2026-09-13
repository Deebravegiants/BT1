# [C] libceph: fix potential use-after-free in have_mon_and_osd_map()

## Summary
Severity: Critical
Advisory: CVE-2025-68285
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-68285
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.35 <5.10.247, >=5.11.0 <5.15.197, >=5.16.0 <6.1.159, >=6.2.0 <6.6.119, >=6.7.0 <6.12.61, >=6.13.0 <6.17.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

libceph: fix potential use-after-free in have_mon_and_osd_map()

The wait loop in __ceph_open_session() can race with the client
receiving a new monmap or osdmap shortly after the initial map is
received.  Both ceph_monc_handle_map() and handle_one_map() install
a new map immediately after freeing the old one

    kfree(monc->monmap);
    monc->monmap = monmap;

    ceph_osdmap_destroy(osdc->osdmap);
    osdc->osdmap = newmap;

under client->monc.mutex and client->osdc.lock respectively, but
because neither is taken in have_mon_and_osd_map() it's possible for
client->monc.monmap->epoch and client->osdc.osdmap->epoch arms in

    client->monc.monmap && client->monc.monmap->epoch &&
        client->osdc.osdmap && client->osdc.osdmap->epoch;

condition to dereference an already freed map.  This happens to be
reproducible with generic/395 and generic/397 with KASAN enabled:

    BUG: KASAN: slab-use-after-free in have_mon_and_osd_map+0x56/0x70
    Read of size 4 at addr ffff88811012d810 by task mount.ceph/13305
    CPU: 2 UID: 0 PID: 13305 Comm: mount.ceph Not tainted 6.14.0-rc2-build2+ #1266
    ...
    Call Trace:
    <TASK>
    have_mon_and_osd_map+0x56/0x70
    ceph_open_session+0x182/0x290
    ceph_get_tree+0x333/0x680
    vfs_get_tree+0x49/0x180
    do_new_mount+0x1a3/0x2d0
    path_mount+0x6dd/0x730
    do_mount+0x99/0xe0
    __do_sys_mount+0x141/0x180
    do_syscall_64+0x9f/0x100
    entry_SYSCALL_64_after_hwframe+0x76/0x7e
    </TASK>

    Allocated by task 13305:
    ceph_osdmap_alloc+0x16/0x130
    ceph_osdc_init+0x27a/0x4c0
    ceph_create_client+0x153/0x190
    create_fs_client+0x50/0x2a0
    ceph_get_tree+0xff/0x680
    vfs_get_tree+0x49/0x180
    do_new_mount+0x1a3/0x2d0
    path_mount+0x6dd/0x730
    do_mount+0x99/0xe0
    __do_sys_mount+0x141/0x180
    do_syscall_64+0x9f/0x100
    entry_SYSCALL_64_after_hwframe+0x76/0x7e

    Freed by task 9475:
    kfree+0x212/0x290
    handle_one_map+0x23c/0x3b0
    ceph_osdc_handle_map+0x3c9/0x590
    mon_dispatch+0x655/0x6f0
    ceph_con_process_message+0xc3/0xe0
    ceph_con_v1_try_read+0x614/0x760
    ceph_con_workfn+0x2de/0x650
    process_one_work+0x486/0x7c0
    process_scheduled_works+0x73/0x90
    worker_thread+0x1c8/0x2a0
    kthread+0x2ec/0x300
    ret_from_fork+0x24/0x40
    ret_from_fork_asm+0x1a/0x30

Rewrite the wait loop to check the above condition directly with
client->monc.mutex and client->osdc.lock taken as appropriate.  While
at it, improve the timeout handling (previously mount_timeout could be
exceeded in case wait_event_interruptible_timeout() slept more than
once) and access client->auth_err under client->monc.mutex to match
how it's set in finish_auth().

monmap_show() and osdmap_show() now take the respective lock before
accessing the map as well.

## References
- https://git.kernel.org/stable/c/05ec43e9a9de67132dc8cd3b22afef001574947f
- https://git.kernel.org/stable/c/076381c261374c587700b3accf410bdd2dba334e
- https://git.kernel.org/stable/c/183ad6e3b651e8fb0b66d6a2678f4b80bfbba092
- https://git.kernel.org/stable/c/3fc43120b22a3d4f1fbeff56a35ce2105b6a5683
- https://git.kernel.org/stable/c/7c8ccdc1714d9fabecd26e1be7db1771061acc6e
- https://git.kernel.org/stable/c/bb4910c5fd436701faf367e1b5476a5a6d2aff1c
- https://git.kernel.org/stable/c/e08021b3b56b2407f37b5fe47b654be80cc665fb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68285.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68285
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
