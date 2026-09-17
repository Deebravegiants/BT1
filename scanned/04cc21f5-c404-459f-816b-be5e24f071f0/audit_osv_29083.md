# [H] kdb: Fix buffer overflow during tab-complete

## Summary
Severity: High
Advisory: CVE-2024-39480
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-05
Source: https://osv.dev/vulnerability/CVE-2024-39480
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.35 <4.19.316, >=4.20.0 <5.4.278, >=5.5.0 <5.10.219, >=5.11.0 <5.15.161, >=5.16.0 <6.1.94, >=6.2.0 <6.6.34, >=6.7.0 <6.9.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

kdb: Fix buffer overflow during tab-complete

Currently, when the user attempts symbol completion with the Tab key, kdb
will use strncpy() to insert the completed symbol into the command buffer.
Unfortunately it passes the size of the source buffer rather than the
destination to strncpy() with predictably horrible results. Most obviously
if the command buffer is already full but cp, the cursor position, is in
the middle of the buffer, then we will write past the end of the supplied
buffer.

Fix this by replacing the dubious strncpy() calls with memmove()/memcpy()
calls plus explicit boundary checks to make sure we have enough space
before we start moving characters around.

## References
- https://git.kernel.org/stable/c/107e825cc448b7834b31e8b1b3cf0f57426d46d5
- https://git.kernel.org/stable/c/33d9c814652b971461d1e30bead6792851c209e7
- https://git.kernel.org/stable/c/cfdc2fa4db57503bc6d3817240547c8ddc55fa96
- https://git.kernel.org/stable/c/ddd2972d8e2dee3b33e8121669d55def59f0be8a
- https://git.kernel.org/stable/c/e9730744bf3af04cda23799029342aa3cddbc454
- https://git.kernel.org/stable/c/f636a40834d22e5e3fc748f060211879c056cd33
- https://git.kernel.org/stable/c/f694da720dcf795dc3eb97bf76d220213f76aaa7
- https://git.kernel.org/stable/c/fb824a99e148ff272a53d71d84122728b5f00992
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39480.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-39480
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
