# [H] nexthop: initialize extack in nh_res_bucket_migrate()

## Summary
Severity: High
Advisory: CVE-2026-64576
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-64576
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

nexthop: initialize extack in nh_res_bucket_migrate()

nh_res_bucket_migrate() passes an uninitialized netlink_ext_ack to
call_nexthop_res_bucket_notifiers(). When
nh_notifier_res_bucket_info_init() fails (e.g. the kzalloc returns
-ENOMEM), the error is propagated back before any notifier sets
extack._msg, and the error path formats the stale pointer with
pr_err_ratelimited("%s\n", extack._msg). With CONFIG_INIT_STACK_NONE
this dereferences uninitialized stack memory:

  Oops: general protection fault, probably for non-canonical address ...
  KASAN: maybe wild-memory-access in range [...]
  RIP: 0010:string (lib/vsprintf.c:730)
   vsnprintf (lib/vsprintf.c:2945)
   _printk (kernel/printk/printk.c:2504)
   nh_res_bucket_migrate (net/ipv4/nexthop.c:1816)
   nh_res_table_upkeep (net/ipv4/nexthop.c:1866)
   rtm_new_nexthop (net/ipv4/nexthop.c:3323)
   rtnetlink_rcv_msg (net/core/rtnetlink.c:7076)
   netlink_sendmsg (net/netlink/af_netlink.c:1900)
  Kernel panic - not syncing: Fatal exception

Zero-initialize extack so _msg is NULL on error paths that never set it.

## References
- https://git.kernel.org/stable/c/18506d7263768d76ac8e057ba55a4d9da50aad66
- https://git.kernel.org/stable/c/3081702ea5aca0aeed9c1ade8eadf6cde8db6b7d
- https://git.kernel.org/stable/c/37bbd7e1d8df0bec3d187e961783e20c30533d2c
- https://git.kernel.org/stable/c/6347c5314cee49f364aaf2e40ff15415a57a116e
- https://git.kernel.org/stable/c/c0936c131a71657afc635d0db2ab096d15d473e1
- https://git.kernel.org/stable/c/d536bf205c71f700f6de2086038c3e1d77724715
- https://git.kernel.org/stable/c/eacd2e2117e8682f937967fda1022e7f1c22d91a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64576.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64576
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
