# [H] drm/vc4: Supply the overflow slot size in BPOS, not the whole bin BO size

## Summary
Severity: High
Advisory: CVE-2026-74454
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74454
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.13.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/vc4: Supply the overflow slot size in BPOS, not the whole bin BO size

vc4_overflow_mem_work() points BPOA at a 512KB slot inside the 16MB
binner BO, but writes the size of the whole BO to BPOS. On every binner
out-of-memory event the PTB is therefore authorized to write tile lists
across all the other slots (which may hold the tile state, tile alloc and
overflow memory of in-flight jobs) and, for any slot but the first, past
the end of the binner BO into unrelated CMA memory.

Since CMA pages are recycled into page cache and user allocations, this
is arbitrary memory corruption by GPU DMA. In practice it shows up as GPU
hangs with corrupted control list pointers, userspace heap corruption, a
GPU that stays permanently wedged after the first hang, and occasional
full system crashes, whenever a job overflows the initial binner slot.

The bug dates back to the conversion from a dedicated overflow BO (where
writing the full BO size was correct) to the slotted binner BO.

## References
- https://git.kernel.org/stable/c/0badb30871004d34df87be33e853536f0b69885f
- https://git.kernel.org/stable/c/1e33ca7f44be64beed2735bb76b86eb65ba8c05b
- https://git.kernel.org/stable/c/2f2291a119e9a8b696ae8bb36e86b75d272ceaea
- https://git.kernel.org/stable/c/6395789e4739aa5177bbec0fa0f07ccc38d249b0
- https://git.kernel.org/stable/c/6cd5acf6f87c073622bd61e38fe99c47365cda9c
- https://git.kernel.org/stable/c/bb5656ae063f2711f56438cf2f1f5b613aea5f12
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74454.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74454
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
