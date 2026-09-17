# [H] fbdev: defio: Disconnect deferred I/O from the lifetime of struct fb_info

## Summary
Severity: High
Advisory: CVE-2026-46065
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-46065
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.22 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.140, >=6.7.0 <6.12.88, >=6.13.0 <6.18.30, >=6.19.0 <7.0.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

fbdev: defio: Disconnect deferred I/O from the lifetime of struct fb_info

Hold state of deferred I/O in struct fb_deferred_io_state. Allocate an
instance as part of initializing deferred I/O and remove it only after
the final mapping has been closed. If the fb_info and the contained
deferred I/O meanwhile goes away, clear struct fb_deferred_io_state.info
to invalidate the mapping. Any access will then result in a SIGBUS
signal.

Fixes a long-standing problem, where a device hot-unplug happens while
user space still has an active mapping of the graphics memory. The hot-
unplug frees the instance of struct fb_info. Accessing the memory will
operate on undefined state.

## References
- https://git.kernel.org/stable/c/25c2b77bc463f29ee71a54b883548baf9386a0db
- https://git.kernel.org/stable/c/2a40f8bc9bb713329f1c35ffc199ee961a7135b0
- https://git.kernel.org/stable/c/2b53d3a52e8e5403a4f4fb57ac6cad3fd2cb1066
- https://git.kernel.org/stable/c/4aab89603b637a2e441b38808c4f6fe7d1184df6
- https://git.kernel.org/stable/c/4fda0d6b45faad44926dd3e4f55f118d899b2e27
- https://git.kernel.org/stable/c/9ded47ad003f09a94b6a710b5c47f4aa5ceb7429
- https://git.kernel.org/stable/c/a0aafb421dd15e935d81543152617f2742cefa70
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46065.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46065
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
