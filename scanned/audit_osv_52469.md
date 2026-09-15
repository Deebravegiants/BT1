# [M] CVE-2021-47482

## Summary
Severity: Medium
Advisory: CVE-2021-47482
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-22
Source: https://osv.dev/vulnerability/CVE-2021-47482
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: batman-adv: fix error handling

Syzbot reported ODEBUG warning in batadv_nc_mesh_free(). The problem was
in wrong error handling in batadv_mesh_init().

Before this patch batadv_mesh_init() was calling batadv_mesh_free() in case
of any batadv_*_init() calls failure. This approach may work well, when
there is some kind of indicator, which can tell which parts of batadv are
initialized; but there isn't any.

All written above lead to cleaning up uninitialized fields. Even if we hide
ODEBUG warning by initializing bat_priv->nc.work, syzbot was able to hit
GPF in batadv_nc_purge_paths(), because hash pointer in still NULL. [1]

To fix these bugs we can unwind batadv_*_init() calls one by one.
It is good approach for 2 reasons: 1) It fixes bugs on error handling
path 2) It improves the performance, since we won't call unneeded
batadv_*_free() functions.

So, this patch makes all batadv_*_init() clean up all allocated memory
before returning with an error to no call correspoing batadv_*_free()
and open-codes batadv_mesh_free() with proper order to avoid touching
uninitialized fields.

## References
- https://git.kernel.org/stable/c/07533f1a673ce1126d0a72ef1e4b5eaaa3dd6d20
- https://git.kernel.org/stable/c/0c6b199f09be489c48622537a550787fc80aea73
- https://git.kernel.org/stable/c/6422e8471890273994fe8cc6d452b0dcd2c9483e
- https://git.kernel.org/stable/c/6f68cd634856f8ca93bafd623ba5357e0f648c68
- https://git.kernel.org/stable/c/a8f7359259dd5923adc6129284fdad12fc5db347
- https://git.kernel.org/stable/c/b0a2cd38553c77928ef1646ed1518486b1e70ae8
- https://git.kernel.org/stable/c/e50f957652190b5a88a8ebce7e5ab14ebd0d3f00
- https://git.kernel.org/stable/c/fbf150b16a3635634b7dfb7f229d8fcd643c6c51
