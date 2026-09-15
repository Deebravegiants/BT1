# [H] ext4: aovid use-after-free in ext4_ext_insert_extent()

## Summary
Severity: High
Advisory: CVE-2024-49883
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-49883
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.18.0 <4.19.323, >=4.20.0 <5.4.285, >=5.5.0 <5.10.227, >=5.11.0 <5.15.168, >=5.16.0 <6.1.113, >=6.2.0 <6.6.55, >=6.7.0 <6.10.14, >=6.11.0 <6.11.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ext4: aovid use-after-free in ext4_ext_insert_extent()

As Ojaswin mentioned in Link, in ext4_ext_insert_extent(), if the path is
reallocated in ext4_ext_create_new_leaf(), we'll use the stale path and
cause UAF. Below is a sample trace with dummy values:

ext4_ext_insert_extent
  path = *ppath = 2000
  ext4_ext_create_new_leaf(ppath)
    ext4_find_extent(ppath)
      path = *ppath = 2000
      if (depth > path[0].p_maxdepth)
            kfree(path = 2000);
            *ppath = path = NULL;
      path = kcalloc() = 3000
      *ppath = 3000;
      return path;
  /* here path is still 2000, UAF! */
  eh = path[depth].p_hdr

==================================================================
BUG: KASAN: slab-use-after-free in ext4_ext_insert_extent+0x26d4/0x3330
Read of size 8 at addr ffff8881027bf7d0 by task kworker/u36:1/179
CPU: 3 UID: 0 PID: 179 Comm: kworker/u6:1 Not tainted 6.11.0-rc2-dirty #866
Call Trace:
 <TASK>
 ext4_ext_insert_extent+0x26d4/0x3330
 ext4_ext_map_blocks+0xe22/0x2d40
 ext4_map_blocks+0x71e/0x1700
 ext4_do_writepages+0x1290/0x2800
[...]

Allocated by task 179:
 ext4_find_extent+0x81c/0x1f70
 ext4_ext_map_blocks+0x146/0x2d40
 ext4_map_blocks+0x71e/0x1700
 ext4_do_writepages+0x1290/0x2800
 ext4_writepages+0x26d/0x4e0
 do_writepages+0x175/0x700
[...]

Freed by task 179:
 kfree+0xcb/0x240
 ext4_find_extent+0x7c0/0x1f70
 ext4_ext_insert_extent+0xa26/0x3330
 ext4_ext_map_blocks+0xe22/0x2d40
 ext4_map_blocks+0x71e/0x1700
 ext4_do_writepages+0x1290/0x2800
 ext4_writepages+0x26d/0x4e0
 do_writepages+0x175/0x700
[...]
==================================================================

So use *ppath to update the path to avoid the above problem.

## References
- https://git.kernel.org/stable/c/51db04892a993cace63415be99848970a0f15ef2
- https://git.kernel.org/stable/c/5e811066c5ab709b070659197dccfb80ab650ddd
- https://git.kernel.org/stable/c/8162ee5d94b8c0351be0a9321be134872a7654a1
- https://git.kernel.org/stable/c/975ca06f3fd154c5f7742083e7b2574c57d1c0c3
- https://git.kernel.org/stable/c/9df59009dfc6d9fc1bd9ddf6c5ab6e56d6ed887a
- https://git.kernel.org/stable/c/a164f3a432aae62ca23d03e6d926b122ee5b860d
- https://git.kernel.org/stable/c/beb7b66fb489041c50c6473100b383f7a51648fc
- https://git.kernel.org/stable/c/bfed082ce4b1ce6349b05c09a0fa4f3da35ecb1b
- https://git.kernel.org/stable/c/e17ebe4fdd7665c93ae9459ba40fcdfb76769ac1
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49883.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-49883
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
