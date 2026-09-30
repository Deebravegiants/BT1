# [H] drm/amdkfd: Fix mode1 reset crash issue

## Summary
Severity: High
Advisory: CVE-2025-37854
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-09
Source: https://osv.dev/vulnerability/CVE-2025-37854
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.135, >=6.2.0 <6.6.88, >=6.7.0 <6.12.24, >=6.13.0 <6.13.12, >=6.14.0 <6.14.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdkfd: Fix mode1 reset crash issue

If HW scheduler hangs and mode1 reset is used to recover GPU, KFD signal
user space to abort the processes. After process abort exit, user queues
still use the GPU to access system memory before h/w is reset while KFD
cleanup worker free system memory and free VRAM.

There is use-after-free race bug that KFD allocate and reuse the freed
system memory, and user queue write to the same system memory to corrupt
the data structure and cause driver crash.

To fix this race, KFD cleanup worker terminate user queues, then flush
reset_domain wq to wait for any GPU ongoing reset complete, and then
free outstanding BOs.

## References
- https://git.kernel.org/stable/c/57c9dabda80ac167de8cd71231baae37cc2f442d
- https://git.kernel.org/stable/c/6f30a847432cae84c7428e9b684b3e3fa49b2391
- https://git.kernel.org/stable/c/89af6b39f028c130d4362f57042927f005423e6a
- https://git.kernel.org/stable/c/9c4bcdf4068aae3e17e31c144300be405cfa03ff
- https://git.kernel.org/stable/c/f0b4440cdc1807bb6ec3dce0d6de81170803569b
- https://git.kernel.org/stable/c/ffd37d7d44d7e0b6e769d4fe6590e327f8cc3951
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37854.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37854
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
