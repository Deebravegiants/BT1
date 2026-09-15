# [H] net: skbuff: fix missing zerocopy reference in pskb_carve helpers

## Summary
Severity: High
Advisory: CVE-2026-52943
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52943
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.7.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: skbuff: fix missing zerocopy reference in pskb_carve helpers

pskb_carve_inside_header() and pskb_carve_inside_nonlinear() both copy
the old skb_shared_info header into a new buffer via memcpy(), which
includes the destructor_arg pointer (uarg) for MSG_ZEROCOPY skbs.
Neither function calls net_zcopy_get() for the new shinfo, creating an
unaccounted holder: every skb_shared_info with destructor_arg set will
call skb_zcopy_clear() once when freed, but the corresponding
net_zcopy_get() was never called for the new copy. Repeated calls
drive uarg->refcnt to zero prematurely, freeing ubuf_info_msgzc while
TX skbs still hold live destructor_arg pointers.

KASAN reports use-after-free on a freed ubuf_info_msgzc:

  BUG: KASAN: slab-use-after-free in skb_release_data+0x77b/0x810
  Read of size 8 at addr ffff88801574d3e8 by task poc/220

  Call Trace:
   skb_release_data+0x77b/0x810
   kfree_skb_list_reason+0x13e/0x610
   skb_release_data+0x4cd/0x810
   sk_skb_reason_drop+0xf3/0x340
   skb_queue_purge_reason+0x282/0x440
   rds_tcp_inc_free+0x1e/0x30
   rds_recvmsg+0x354/0x1780
   __sys_recvmsg+0xdf/0x180

  Allocated by task 219:
   msg_zerocopy_realloc+0x157/0x7b0
   tcp_sendmsg_locked+0x2892/0x3ba0

  Freed by task 219:
   ip_recv_error+0x74a/0xb10
   tcp_recvmsg+0x475/0x530

The skb consuming the late access still referenced the same uarg via
shinfo->destructor_arg copied by pskb_carve_inside_nonlinear() without
a refcount bump. This has been verified to be reliably exploitable: a
working proof-of-concept achieves full root privilege escalation from
an unprivileged local user on a default kernel configuration.

The fix follows the pattern of pskb_expand_head() which has the same
memcpy/cloned structure. For pskb_carve_inside_header(), net_zcopy_get()
is placed after skb_orphan_frags() succeeds, so the orphan error path
needs no cleanup. For pskb_carve_inside_nonlinear(), net_zcopy_get() is
placed after all failure points and just before skb_release_data(), so
no error path needs cleanup at all -- matching pskb_expand_head() more
closely and avoiding the need for a balancing net_zcopy_put().

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/2e0e74c59b2761a414d9f48d7bee1e45220b2427
- https://git.kernel.org/stable/c/474d6c771d798bca84f0a140b611e36743511e18
- https://git.kernel.org/stable/c/8dbed691e43a50903658130bde0fcb5abc425b37
- https://git.kernel.org/stable/c/96a4713ae041cc85e712bac682cd2e644004d6c6
- https://git.kernel.org/stable/c/98d0912e9f841e5529a5b89a972805f34cb1c69d
- https://git.kernel.org/stable/c/9b40bdc2a3298225dffab8158208a0d8c6300578
- https://git.kernel.org/stable/c/ceafb893b12f23331dcc5ff9587e643c3a40ee9f
- https://git.kernel.org/stable/c/fd470f0a97b8e9a125f520265d2f3b088ffb5b8a
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-52943.json
- https://access.redhat.com/security/cve/CVE-2026-52943
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52943.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52943
- https://bugzilla.redhat.com/show_bug.cgi?id=2492137
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
