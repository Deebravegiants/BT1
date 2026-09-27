# [M] do_sys_name_to_handle(): use kzalloc() to fix kernel-infoleak

## Summary
Severity: Medium
Advisory: CVE-2024-26901
Ecosystem: Linux
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-04-17
Source: https://osv.dev/vulnerability/CVE-2024-26901
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.39 <4.19.311, >=4.20.0 <5.4.273, >=5.5.0 <5.10.214, >=5.11.0 <5.15.153, >=5.16.0 <6.1.83, >=6.2.0 <6.6.23, >=6.7.0 <6.7.11, >=6.8.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

do_sys_name_to_handle(): use kzalloc() to fix kernel-infoleak

syzbot identified a kernel information leak vulnerability in
do_sys_name_to_handle() and issued the following report [1].

[1]
"BUG: KMSAN: kernel-infoleak in instrument_copy_to_user include/linux/instrumented.h:114 [inline]
BUG: KMSAN: kernel-infoleak in _copy_to_user+0xbc/0x100 lib/usercopy.c:40
 instrument_copy_to_user include/linux/instrumented.h:114 [inline]
 _copy_to_user+0xbc/0x100 lib/usercopy.c:40
 copy_to_user include/linux/uaccess.h:191 [inline]
 do_sys_name_to_handle fs/fhandle.c:73 [inline]
 __do_sys_name_to_handle_at fs/fhandle.c:112 [inline]
 __se_sys_name_to_handle_at+0x949/0xb10 fs/fhandle.c:94
 __x64_sys_name_to_handle_at+0xe4/0x140 fs/fhandle.c:94
 ...

Uninit was created at:
 slab_post_alloc_hook+0x129/0xa70 mm/slab.h:768
 slab_alloc_node mm/slub.c:3478 [inline]
 __kmem_cache_alloc_node+0x5c9/0x970 mm/slub.c:3517
 __do_kmalloc_node mm/slab_common.c:1006 [inline]
 __kmalloc+0x121/0x3c0 mm/slab_common.c:1020
 kmalloc include/linux/slab.h:604 [inline]
 do_sys_name_to_handle fs/fhandle.c:39 [inline]
 __do_sys_name_to_handle_at fs/fhandle.c:112 [inline]
 __se_sys_name_to_handle_at+0x441/0xb10 fs/fhandle.c:94
 __x64_sys_name_to_handle_at+0xe4/0x140 fs/fhandle.c:94
 ...

Bytes 18-19 of 20 are uninitialized
Memory access of size 20 starts at ffff888128a46380
Data copied to user address 0000000020000240"

Per Chuck Lever's suggestion, use kzalloc() instead of kmalloc() to
solve the problem.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-398330.html
- https://git.kernel.org/stable/c/3948abaa4e2be938ccdfc289385a27342fb13d43
- https://git.kernel.org/stable/c/423b6bdf19bbc5e1f7e7461045099917378f7e71
- https://git.kernel.org/stable/c/4bac28f441e3cc9d3f1a84c8d023228a68d8a7c1
- https://git.kernel.org/stable/c/772a7def9868091da3bcb0d6c6ff9f0c03d7fa8b
- https://git.kernel.org/stable/c/bf9ec1b24ab4e94345aa1c60811dd329f069c38b
- https://git.kernel.org/stable/c/c1362eae861db28b1608b9dc23e49634fe87b63b
- https://git.kernel.org/stable/c/cba138f1ef37ec6f961baeab62f312dedc7cf730
- https://git.kernel.org/stable/c/cde76b3af247f615447bcfecf610bb76c3529126
- https://git.kernel.org/stable/c/e6450d5e46a737a008b4885aa223486113bf0ad6
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26901.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26901
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
