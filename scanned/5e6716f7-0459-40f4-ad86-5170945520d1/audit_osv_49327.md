# [C] CVE-2019-10125

## Summary
Severity: Critical
Advisory: CVE-2019-10125
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-03-27
Source: https://osv.dev/vulnerability/CVE-2019-10125
Type: osv

## Details
An issue was discovered in aio_poll() in fs/aio.c in the Linux kernel through 5.0.4. A file may be released by aio_poll_wake() if an expected event is triggered immediately (e.g., by the close of a pair of pipes) after the return of vfs_poll(), and this will cause a use-after-free.

## References
- http://www.securityfocus.com/bid/107655
- https://security.netapp.com/advisory/ntap-20190411-0003/
- https://support.f5.com/csp/article/K29215970
- https://patchwork.kernel.org/patch/10828359/
