# [H] JLSEC-2026-518

## Summary
Severity: High
Advisory: JLSEC-2026-518
Ecosystem: Julia
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/JLSEC-2026-518
Type: osv

## Affected
- Julia: `GnuTLS_jll` — affected >=0 <3.7.1+0

## Details
GnuTLS 3.6.x before 3.6.14 uses incorrect cryptography for encrypting a session ticket (a loss of confidentiality in TLS 1.2, and an authentication bypass in TLS 1.3). The earliest affected version is 3.6.4 (2018-09-24) because of an error in a 2018-09-18 commit. Until the first key rotation, the TLS server always uses wrong data in place of an encryption key derived from an application.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00015.html
- https://gnutls.org/security-new.html#GNUTLS-SA-2020-06-03
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6C4DHUKV6M6SJ5CV6KVHZNHNF7HCUE5P/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6RTXZOXC4MHTFE2HKY6IAZMF2WHD2WMV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RRQBFK3UZ7SV76IYDTS4PS6ABS2DSJHK/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VMB3UGI5H5RCFRU6OGRPMNUCNLJGEN7Y/
- https://security.gentoo.org/glsa/202006-01
- https://security.netapp.com/advisory/ntap-20200619-0004/
- https://usn.ubuntu.com/4384-1/
- https://www.debian.org/security/2020/dsa-4697
