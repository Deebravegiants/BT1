# [H] dma-fence: Make dma_fence_dedup_array() robust against 0-count input

## Summary
Severity: High
Advisory: CVE-2026-72095
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72095
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

dma-fence: Make dma_fence_dedup_array() robust against 0-count input

dma_fence_dedup_array() returns 1 when called with num_fences == 0:
the for-loop body never executes, j stays at 0, and the final
`return ++j` yields 1. This contradicts both the kernel-doc ("Return:
Number of unique fences remaining in the array") and the natural
expectation that 0 input gives 0 output.

The caller __dma_fence_unwrap_merge() bails out via the
`if (count == 0 || count == 1)` fast path and so is save.

But amdgpu_userq_wait_*() could reach the dedup call with a zero local
count and dereference an uninitialized fence slot in the array.

Make the contract match the documentation by returning 0 early. This
also skips an unnecessary sort() call on an empty array.

## References
- https://git.kernel.org/stable/c/77a9298741f8f9e8b963c977f5582ab21c6d3427
- https://git.kernel.org/stable/c/7aa8f3dba53422465dbe1be8dbb7240304462bb2
- https://git.kernel.org/stable/c/e2d9a2ea178a5da0b4a6693e8ebca5c7fc4d7051
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72095.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72095
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
