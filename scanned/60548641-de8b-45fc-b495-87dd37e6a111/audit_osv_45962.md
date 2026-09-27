# [M] JLSEC-2026-522

## Summary
Severity: Medium
Advisory: JLSEC-2026-522
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/JLSEC-2026-522
Type: osv

## Affected
- Julia: `GnuTLS_jll` — affected >=0 <3.7.8+0

## Details
A NULL pointer dereference flaw was found in GnuTLS. As Nettle's hash update functions internally call memcpy, providing zero-length input may cause undefined behavior. This flaw leads to a denial of service after authentication in rare circumstances.

## References
- https://access.redhat.com/security/cve/CVE-2021-4209
- https://bugzilla.redhat.com/show_bug.cgi?id=2044156
- https://gitlab.com/gnutls/gnutls/-/commit/3db352734472d851318944db13be73da61300568
- https://gitlab.com/gnutls/gnutls/-/issues/1306
- https://gitlab.com/gnutls/gnutls/-/merge_requests/1503
- https://security.netapp.com/advisory/ntap-20220915-0005/
