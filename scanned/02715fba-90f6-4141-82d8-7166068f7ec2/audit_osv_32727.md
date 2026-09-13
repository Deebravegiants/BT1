# [C] ksmbd: Fix dangling pointer in krb_authenticate

## Summary
Severity: Critical
Advisory: CVE-2025-37778
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2025-37778
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.203, >=5.16.0 <6.1.135, >=6.2.0 <6.6.88, >=6.7.0 <6.12.25, >=6.13.0 <6.14.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: Fix dangling pointer in krb_authenticate

krb_authenticate frees sess->user and does not set the pointer
to NULL. It calls ksmbd_krb5_authenticate to reinitialise
sess->user but that function may return without doing so. If
that happens then smb2_sess_setup, which calls krb_authenticate,
will be accessing free'd memory when it later uses sess->user.

## References
- https://git.kernel.org/stable/c/1db2451de23e98bc864c6a6e52aa0d82c91cb325
- https://git.kernel.org/stable/c/1e440d5b25b7efccb3defe542a73c51005799a5f
- https://git.kernel.org/stable/c/6e30c0e10210c714f3d4453dc258d4abcc70364e
- https://git.kernel.org/stable/c/b61f04d5d73c53d183019bafe22fb700a739bac5
- https://git.kernel.org/stable/c/d5b554bc8d554ed6ddf443d3db2fad9f665cec10
- https://git.kernel.org/stable/c/e83e39a5f6a01a81411a4558a59a10f87aa88dd6
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37778.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37778
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
