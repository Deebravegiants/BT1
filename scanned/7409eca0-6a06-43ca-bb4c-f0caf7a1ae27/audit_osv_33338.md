# [H] Bluetooth: ISO: Fix possible UAF on iso_conn_free

## Summary
Severity: High
Advisory: CVE-2025-40141
Ecosystem: Linux
CVSS: 8.0 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-12
Source: https://osv.dev/vulnerability/CVE-2025-40141
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.156, >=6.2.0 <6.6.112, >=6.7.0 <6.12.53, >=6.13.0 <6.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: ISO: Fix possible UAF on iso_conn_free

This attempt to fix similar issue to sco_conn_free where if the
conn->sk is not set to NULL may lead to UAF on iso_conn_free.

## References
- https://git.kernel.org/stable/c/5319145a07d8bf5b0782b25cb3115825689d42bb
- https://git.kernel.org/stable/c/80689777919f02328eb873769de4647c9dd3e371
- https://git.kernel.org/stable/c/9950f095d6c875dbe0c9ebfcf972ec88fdf26fc8
- https://git.kernel.org/stable/c/c92ad1a155ccfa38b87bd1d998287e1c0a24248d
- https://git.kernel.org/stable/c/eba6d787ec117a5d2c60f9644e0a39c18542b6be
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40141.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40141
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
