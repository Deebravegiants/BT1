# [H] drm/vmwgfx: Fix Use-after-free in validation

## Summary
Severity: High
Advisory: CVE-2025-40111
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-12
Source: https://osv.dev/vulnerability/CVE-2025-40111
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.4.301, >=5.5.0 <5.10.246, >=5.11.0 <5.15.195, >=5.16.0 <6.1.157, >=6.2.0 <6.6.113, >=6.7.0 <6.12.54, >=6.13.0 <6.17.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/vmwgfx: Fix Use-after-free in validation

Nodes stored in the validation duplicates hashtable come from an arena
allocator that is cleared at the end of vmw_execbuf_process. All nodes
are expected to be cleared in vmw_validation_drop_ht but this node escaped
because its resource was destroyed prematurely.

## References
- https://git.kernel.org/stable/c/1822e5287b7dfa59d0af966756ebf1dc652b60ee
- https://git.kernel.org/stable/c/4c918f9d1ccccc0e092f43dcb2d8266f54d7340b
- https://git.kernel.org/stable/c/655a2f29bfc21105c80bf8a7d7aafa6eca8b4496
- https://git.kernel.org/stable/c/65608e991c2d771c13404e5c7ae122ac3c3357a4
- https://git.kernel.org/stable/c/867bda5d95d36f10da398fd4409e21c7002b2332
- https://git.kernel.org/stable/c/9a8eaca539708ca532747f606d231f70e684e8ca
- https://git.kernel.org/stable/c/dfe1323ab3c8a4dd5625ebfdba44dc47df84512a
- https://git.kernel.org/stable/c/fb7165e5f3b3b10721ff70553583ad12e90e447a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40111.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40111
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
