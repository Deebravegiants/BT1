# [C] libceph: bound pg_{temp,upmap,upmap_items} length to CEPH_PG_MAX_SIZE

## Summary
Severity: Critical
Advisory: CVE-2026-68159
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68159
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.13.0 <5.10.266, >=5.11.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.153, >=6.7.0 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

libceph: bound pg_{temp,upmap,upmap_items} length to CEPH_PG_MAX_SIZE

__decode_pg_temp() decodes an user-controlled length but only rejects
values large enough to overflow the allocation; it does not bound it to
CEPH_PG_MAX_SIZE. The helper backs both pg_temp and pg_upmap decoding, and
apply_upmap()/get_temp_osds() later copy the decoded list into the fixed-size
on-stack array struct ceph_osds.osds[CEPH_PG_MAX_SIZE]. A monitor that sends
an OSDMap with a pg_temp/pg_upmap entry longer than 32 thus causes a stack
out-of-bounds write.

An OSD set for a single PG can never exceed CEPH_PG_MAX_SIZE, so reject longer
entries at decode time. The bound is well below the old overflow threshold, so
it also covers the allocation-size overflow the previous check guarded against.

  BUG: KASAN: stack-out-of-bounds in ceph_pg_to_up_acting_osds
  Write of size 4 ... by task exploit
   kasan_report (mm/kasan/report.c:595)
   ceph_pg_to_up_acting_osds (net/ceph/osdmap.c:2617 net/ceph/osdmap.c:2833)
   calc_target (net/ceph/osd_client.c:1638)
   __submit_request (net/ceph/osd_client.c:2394)
   ceph_osdc_start_request (net/ceph/osd_client.c:2490)
   ceph_osdc_call (net/ceph/osd_client.c:5164)
   rbd_dev_image_probe (drivers/block/rbd.c:6899)
   do_rbd_add (drivers/block/rbd.c:7138)
   ...
  kernel BUG at net/ceph/osdmap.c:2670!

[ idryomov: do the same in __decode_pg_upmap_items() ]

## References
- https://git.kernel.org/stable/c/42bc06c67d94d5f2a6b33294b0c4b07d8a47c515
- https://git.kernel.org/stable/c/4daf06456677177f2a6044729abac59c1b49e87b
- https://git.kernel.org/stable/c/590b07ceea138d49c9b64f65d263aa902d3b4730
- https://git.kernel.org/stable/c/66eec4af1e080b695229c9a20635648a6d12fedf
- https://git.kernel.org/stable/c/9f00f9cf2be293efe899db67dc5272e3a9c62717
- https://git.kernel.org/stable/c/d5650ddbd4d42c1a916c8fe1a4c4cb573ef810a1
- https://git.kernel.org/stable/c/e36663145abd7024f0281dfb22fdef65f185845b
- https://git.kernel.org/stable/c/ebdf4b4f3b1474079980a2e5cd79ad65fb54db57
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68159.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68159
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
