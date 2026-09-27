# [H] drm/amdgpu/vce: fix integer overflow in image size

## Summary
Severity: High
Advisory: CVE-2026-68108
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68108
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu/vce: fix integer overflow in image size

Fix a security vulnerability where malicious VCE command streams
with oversized dimensions (e.g. 65536×65536) cause 32-bit integer
overflow, wrapping the calculated buffer size to 0. This bypasses
validation and allows GPU firmware to perform out-of-bound memory
access.

The fix uses 64-bit arithmetic to detect overflow and rejects
invalid dimensions before they reach the hardware.

V2: remove redundant check
V3: modify max height value
V4: remove size64

(cherry picked from commit cbe408dba581755ad1279a487ec786d8927d778d)

## References
- https://git.kernel.org/stable/c/00c311a13d225266800c712f2b7db2711c6897de
- https://git.kernel.org/stable/c/186bfdc4e26d019b2e7570cb121964a1d89b2e5b
- https://git.kernel.org/stable/c/7eebef042c12dfe0568593ee6a8926d16505925e
- https://git.kernel.org/stable/c/893db20383800cfe92e638705984eebb13bc81a5
- https://git.kernel.org/stable/c/a07430abd556de3707adfcadcc60db3fa64e4b2b
- https://git.kernel.org/stable/c/a6d7065b91a14790980ce6f4960db0ca8c3c9940
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68108.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68108
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
