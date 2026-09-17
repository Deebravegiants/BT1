# [H] net: libwx: handle page_pool_dev_alloc_pages error

## Summary
Severity: High
Advisory: CVE-2025-37755
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2025-37755
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.88, >=6.7.0 <6.12.24, >=6.13.0 <6.13.12, >=6.14.0 <6.14.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: libwx: handle page_pool_dev_alloc_pages error

page_pool_dev_alloc_pages could return NULL. There was a WARN_ON(!page)
but it would still proceed to use the NULL pointer and then crash.

This is similar to commit 001ba0902046
("net: fec: handle page_pool_dev_alloc_pages error").

This is found by our static analysis tool KNighter.

## References
- https://git.kernel.org/stable/c/1dd13c60348f515acd8c6f25a561b9c4e3b04fea
- https://git.kernel.org/stable/c/7f1ff1b38a7c8b872382b796023419d87d78c47e
- https://git.kernel.org/stable/c/90bec7cef8805f9a23145e070dff28a02bb584eb
- https://git.kernel.org/stable/c/ad81d666e114ebf989fc9994d4c93d451dc60056
- https://git.kernel.org/stable/c/c17ef974bfcf1a50818168b47c4606b425a957c4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37755.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37755
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
