# [H] ksmbd: prevent rename with empty string

## Summary
Severity: High
Advisory: CVE-2025-37956
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-20
Source: https://osv.dev/vulnerability/CVE-2025-37956
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.6.91, >=6.7.0 <6.12.29, >=6.13.0 <6.14.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: prevent rename with empty string

Client can send empty newname string to ksmbd server.
It will cause a kernel oops from d_alloc.
This patch return the error when attempting to rename
a file or directory with an empty new name string.

## References
- https://git.kernel.org/stable/c/53e3e5babc0963a92d856a5ec0ce92c59f54bc12
- https://git.kernel.org/stable/c/6ee551672c8cf36108b0cfba92ec0c7c28ac3439
- https://git.kernel.org/stable/c/c57301e332cc413fe0a7294a90725f4e21e9549d
- https://git.kernel.org/stable/c/d7f2c00acb1ef64304fd40ac507e9213ff1d9b5c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37956.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37956
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
