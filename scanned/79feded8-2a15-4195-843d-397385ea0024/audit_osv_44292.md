# [H] drm/log: Fix out-of-bounds read on empty message length

## Summary
Severity: High
Advisory: CVE-2026-80741
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-80741
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/log: Fix out-of-bounds read on empty message length

drm_log_draw_kmsg_record() accesses s[len - 1] to strip the trailing
newline, but len is unsigned int. If len is 0, the subtraction wraps
to UINT_MAX, causing an out-of-bounds read.

Add an early return when len is 0.

## References
- https://git.kernel.org/stable/c/16a2716910ecf7d31bf3c033ee7c506a0b00b2ee
- https://git.kernel.org/stable/c/16bcea56f4205314ec2aa04a7ec74e5261d253c7
- https://git.kernel.org/stable/c/60baa179ed1333535f6e2da4133511db55278ee4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80741.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80741
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
