# [H] drm/amdgpu: Fix fence put before wait in amdgpu_amdkfd_submit_ib

## Summary
Severity: High
Advisory: CVE-2026-31566
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31566
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.168, >=6.2.0 <6.6.131, >=6.7.0 <6.12.80, >=6.13.0 <6.18.21, >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: Fix fence put before wait in amdgpu_amdkfd_submit_ib

amdgpu_amdkfd_submit_ib() submits a GPU job and gets a fence
from amdgpu_ib_schedule(). This fence is used to wait for job
completion.

Currently, the code drops the fence reference using dma_fence_put()
before calling dma_fence_wait().

If dma_fence_put() releases the last reference, the fence may be
freed before dma_fence_wait() is called. This can lead to a
use-after-free.

Fix this by waiting on the fence first and releasing the reference
only after dma_fence_wait() completes.

Fixes the below:
drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd.c:697 amdgpu_amdkfd_submit_ib() warn: passing freed memory 'f' (line 696)

(cherry picked from commit 8b9e5259adc385b61a6590a13b82ae0ac2bd3482)

## References
- https://git.kernel.org/stable/c/138e42be35ff2ce6572ae744de851ea286cf3c69
- https://git.kernel.org/stable/c/39820864eacd886f1a6f817414fb8f9ea3e9a2b4
- https://git.kernel.org/stable/c/42d248726a0837640452b71c5a202ca3d35239ec
- https://git.kernel.org/stable/c/7150850146ebfa4ca998f653f264b8df6f7f85be
- https://git.kernel.org/stable/c/bc7760c107dc08ef3e231d72c492e67b0a86848b
- https://git.kernel.org/stable/c/e23602eb0779760544314ed3905fa6a89a4e4070
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31566.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31566
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
