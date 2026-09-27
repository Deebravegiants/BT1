# [H] CVE-2020-11501

## Summary
Severity: High
Advisory: CVE-2020-11501
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2020-04-03
Source: https://osv.dev/vulnerability/CVE-2020-11501
Type: osv

## Details
GnuTLS 3.6.x before 3.6.13 uses incorrect cryptography for DTLS. The earliest affected version is 3.6.3 (2018-07-16) because of an error in a 2017-10-06 commit. The DTLS client always uses 32 '\0' bytes instead of a random value, and thus contributes no randomness to a DTLS negotiation. This breaks the security guarantees of the DTLS protocol.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ILMOWPKMTZAIMK5F32TUMO34XCABUCFJ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WDYY3R4F5CUTFAMXH2C5NKYFVDEJLTT7/
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00015.html
- https://security.gentoo.org/glsa/202004-06
- https://security.netapp.com/advisory/ntap-20200416-0002/
- https://usn.ubuntu.com/4322-1/
- https://www.debian.org/security/2020/dsa-4652
- https://www.gnutls.org/security-new.html#GNUTLS-SA-2020-03-31
- https://gitlab.com/gnutls/gnutls/-/commit/5b595e8e52653f6c5726a4cdd8fddeb6e83804d2
- https://gitlab.com/gnutls/gnutls/-/issues/960
