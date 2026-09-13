# [M] media: uvcvideo: Fix deadlock during uvc_probe

## Summary
Severity: Medium
Advisory: CVE-2024-58059
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-06
Source: https://osv.dev/vulnerability/CVE-2024-58059
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: uvcvideo: Fix deadlock during uvc_probe

If uvc_probe() fails, it can end up calling uvc_status_unregister() before
uvc_status_init() is called.

Fix this by checking if dev->status is NULL or not in
uvc_status_unregister().

## References
- https://git.kernel.org/stable/c/a67f75c2b5ecf534eab416ce16c11fe780c4f8f6
- https://git.kernel.org/stable/c/db577ededf3a18b39567fc1a6209f12a0c4a3c52
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58059.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58059
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
