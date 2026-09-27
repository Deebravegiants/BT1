# [H] ksmbd: fix null pointer dereference in alloc_preauth_hash()

## Summary
Severity: High
Advisory: CVE-2025-22037
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22037
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.6.107, >=6.7.0 <6.12.23, >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix null pointer dereference in alloc_preauth_hash()

The Client send malformed smb2 negotiate request. ksmbd return error
response. Subsequently, the client can send smb2 session setup even
thought conn->preauth_info is not allocated.
This patch add KSMBD_SESS_NEED_SETUP status of connection to ignore
session setup request if smb2 negotiate phase is not complete.

## References
- https://git.kernel.org/stable/c/8f216b33a5e1b3489c073b1ea1b3d7cb63c8dc4d
- https://git.kernel.org/stable/c/b8eb243e670ecf30e91524dd12f7260dac07d335
- https://git.kernel.org/stable/c/c8b5b7c5da7d0c31c9b7190b4a7bba5281fc4780
- https://git.kernel.org/stable/c/ca8bed31edf728a662ef9d6f39f50e7a7dc2b5ad
- https://git.kernel.org/stable/c/cce57cd8c5dead24127cf2308fdd60fcad2d6ba6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22037.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22037
- https://www.zerodayinitiative.com/advisories/ZDI-25-310/
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
