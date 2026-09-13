# [H] accel/ethosu: reject DMA commands with uninitialized length

## Summary
Severity: High
Advisory: CVE-2026-53170
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53170
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

accel/ethosu: reject DMA commands with uninitialized length

cmd_state_init() initializes the command state with memset(0xff),
leaving dma->len at U64_MAX to signal missing setup. The only setter
is NPU_SET_DMA0_LEN; if userspace omits this command and issues
NPU_OP_DMA_START, dma->len remains U64_MAX.

In dma_length(), a positive stride added to U64_MAX wraps to a small
value. With size0 == 1, check_mul_overflow() does not trigger and
dma_length() returns 0 instead of U64_MAX. The caller's U64_MAX check
then passes, region_size[] stays 0, and the bounds check in
ethosu_job.c is bypassed, allowing hardware to execute DMA with stale
physical addresses.

Fix by checking for U64_MAX at the start of dma_length() before any
arithmetic, consistent with the sentinel value used throughout the
driver to detect uninitialized fields.

## References
- https://git.kernel.org/stable/c/d9d021218162b6c4fe0bdf42b2b340f1aae23a12
- https://git.kernel.org/stable/c/fb25c76a820ca8a547aa478bfb503da0a11494ab
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53170.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53170
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
