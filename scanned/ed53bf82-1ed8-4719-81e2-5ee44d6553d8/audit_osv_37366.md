# [H] ksmbd: unset conn->binding on failed binding request

## Summary
Severity: High
Advisory: CVE-2026-31409
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-06
Source: https://osv.dev/vulnerability/CVE-2026-31409
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.209, >=5.16.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.20, >=6.19.0 <6.19.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: unset conn->binding on failed binding request

When a multichannel SMB2_SESSION_SETUP request with
SMB2_SESSION_REQ_FLAG_BINDING fails ksmbd sets conn->binding = true
but never clears it on the error path. This leaves the connection in
a binding state where all subsequent ksmbd_session_lookup_all() calls
fall back to the global sessions table. This fix it by clearing
conn->binding = false in the error path.

## References
- https://git.kernel.org/stable/c/282343cf8a4a5a3603b1cb0e17a7083e4a593b03
- https://git.kernel.org/stable/c/6260fc85ed1298a71d24a75d01f8b2e56d489a60
- https://git.kernel.org/stable/c/6ebef4a220a1ebe345de899ebb9ae394206fe921
- https://git.kernel.org/stable/c/7e8b270813079c785696bce8802a3f920665c88c
- https://git.kernel.org/stable/c/89afe5e2dbea6e9d8e5f11324149d06fa3a4efca
- https://git.kernel.org/stable/c/9feb2d1bf86d9e5e66b8565f37f8d3a7d281a772
- https://git.kernel.org/stable/c/d073870dab8f6dadced81d13d273ff0b21cb7f4e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31409.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31409
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
