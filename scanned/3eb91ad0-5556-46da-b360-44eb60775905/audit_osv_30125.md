# [H] drm/xe/oa: Fix overflow in oa batch buffer

## Summary
Severity: High
Advisory: CVE-2024-50090
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-05
Source: https://osv.dev/vulnerability/CVE-2024-50090
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.11.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe/oa: Fix overflow in oa batch buffer

By default xe_bb_create_job() appends a MI_BATCH_BUFFER_END to batch
buffer, this is not a problem if batch buffer is only used once but
oa reuses the batch buffer for the same metric and at each call
it appends a MI_BATCH_BUFFER_END, printing the warning below and then
overflowing.

[  381.072016] ------------[ cut here ]------------
[  381.072019] xe 0000:00:02.0: [drm] Assertion `bb->len * 4 + bb_prefetch(q->gt) <= size` failed!
               platform: LUNARLAKE subplatform: 1
               graphics: Xe2_LPG / Xe2_HPG 20.04 step B0
               media: Xe2_LPM / Xe2_HPM 20.00 step B0
               tile: 0 VRAM 0 B
               GT: 0 type 1

So here checking if batch buffer already have MI_BATCH_BUFFER_END if
not append it.

v2:
- simply fix, suggestion from Ashutosh

(cherry picked from commit 9ba0e0f30ca42a98af3689460063edfb6315718a)

## References
- https://git.kernel.org/stable/c/6c10ba06bb1b48acce6d4d9c1e33beb9954f1788
- https://git.kernel.org/stable/c/bcb5be3421705e682b0b32073ad627056d6bc2a2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50090.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50090
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
