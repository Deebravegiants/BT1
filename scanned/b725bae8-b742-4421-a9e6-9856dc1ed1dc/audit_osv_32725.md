# [H] ksmbd: fix use-after-free in smb_break_all_levII_oplock()

## Summary
Severity: High
Advisory: CVE-2025-37776
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2025-37776
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.6.88, >=6.7.0 <6.12.25, >=6.13.0 <6.14.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix use-after-free in smb_break_all_levII_oplock()

There is a room in smb_break_all_levII_oplock that can cause racy issues
when unlocking in the middle of the loop. This patch use read lock
to protect whole loop.

## References
- https://git.kernel.org/stable/c/18b4fac5ef17f77fed9417d22210ceafd6525fc7
- https://git.kernel.org/stable/c/296cb5457cc6f4a754c4ae29855f8a253d52bcc6
- https://git.kernel.org/stable/c/d54ab1520d43e95f9b2e22d7a05fc9614192e5a5
- https://git.kernel.org/stable/c/d73686367ad68534257cd88a36ca3c52cb8b81d8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37776.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37776
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
