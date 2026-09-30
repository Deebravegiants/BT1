# [H] ksmbd: fix possible memory leak in smb2_lock()

## Summary
Severity: High
Advisory: CVE-2023-54162
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-30
Source: https://osv.dev/vulnerability/CVE-2023-54162
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.145, >=5.16.0 <6.1.16, >=6.2.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix possible memory leak in smb2_lock()

argv needs to be free when setup_async_work fails or when the current
process is woken up.

## References
- https://git.kernel.org/stable/c/11d38f8a0c19763e34d2093b5ecb640e012cb2d2
- https://git.kernel.org/stable/c/6bf555ed8938444466c3d7f3252eb874a518f293
- https://git.kernel.org/stable/c/bfe8372ef2dbdce97f13b21d76e2080ddeef5a79
- https://git.kernel.org/stable/c/d3ca9f7aeba793d74361d88a8800b2f205c9236b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54162.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54162
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
