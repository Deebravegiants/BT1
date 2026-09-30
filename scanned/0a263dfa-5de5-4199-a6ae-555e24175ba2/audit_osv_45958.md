# [H] JLSEC-2026-519

## Summary
Severity: High
Advisory: JLSEC-2026-519
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/JLSEC-2026-519
Type: osv

## Affected
- Julia: `GnuTLS_jll` — affected >=0 <3.7.1+0

## Details
An issue was discovered in GnuTLS before 3.6.15. A server can trigger a NULL pointer dereference in a TLS 1.3 client if a `no_renegotiation` alert is sent with unexpected timing, and then an invalid second handshake occurs. The crash happens in the application's error handling path, where the `gnutls_deinit` function is called after detecting a handshake failure.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00054.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00060.html
- https://gitlab.com/gnutls/gnutls/-/issues/1071
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/62BUAI4FQQLG6VTKRT7SUZPGJJ4NASQ3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AWN56FDLQQXT2D2YHNI4TYH432TDMQ7N/
- https://security.gentoo.org/glsa/202009-01
- https://security.netapp.com/advisory/ntap-20200911-0006/
- https://usn.ubuntu.com/4491-1/
- https://www.gnutls.org/security-new.html#GNUTLS-SA-2020-09-04
