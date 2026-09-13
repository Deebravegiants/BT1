# [H] ksmbd: validate request buffer size in smb2_allocate_rsp_buf()

## Summary
Severity: High
Advisory: CVE-2024-26936
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-26936
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.159, >=5.16.0 <6.1.88, >=6.2.0 <6.6.29, >=6.7.0 <6.8.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: validate request buffer size in smb2_allocate_rsp_buf()

The response buffer should be allocated in smb2_allocate_rsp_buf
before validating request. But the fields in payload as well as smb2 header
is used in smb2_allocate_rsp_buf(). This patch add simple buffer size
validation to avoid potencial out-of-bounds in request buffer.

## References
- https://git.kernel.org/stable/c/17cf0c2794bdb6f39671265aa18aea5c22ee8c4a
- https://git.kernel.org/stable/c/21ff9d7d223c5c19cb4334009e4c0c83a2f4d674
- https://git.kernel.org/stable/c/2c27a64a2bc47d9bfc7c3cf8be14be53b1ee7cb6
- https://git.kernel.org/stable/c/5c20b242d4fed73a93591e48bfd9772e2322fb11
- https://git.kernel.org/stable/c/8f3d0bf1d0c62b539d54c5b9108a845cff619b99
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26936.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26936
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
