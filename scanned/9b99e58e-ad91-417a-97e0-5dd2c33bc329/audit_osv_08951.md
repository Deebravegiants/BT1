# [M] CVE-2016-7056

## Summary
Severity: Medium
Advisory: CVE-2016-7056
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-09-10
Source: https://osv.dev/vulnerability/CVE-2016-7056
Type: osv

## Details
A timing attack flaw was found in OpenSSL 1.0.1u and before that could allow a malicious user with local access to recover ECDSA P-256 private keys.

## References
- https://git.openssl.org/?p=openssl.git%3Ba=commit%3Bh=8aed2a7548362e88e84a7feb795a3a97e8395008
- http://rhn.redhat.com/errata/RHSA-2017-1415.html
- http://www.securityfocus.com/bid/95375
- https://access.redhat.com/errata/RHSA-2017:1413
- https://access.redhat.com/errata/RHSA-2017:1414
- https://access.redhat.com/errata/RHSA-2017:1801
- https://access.redhat.com/errata/RHSA-2017:1802
- https://eprint.iacr.org/2016/1195
- https://seclists.org/oss-sec/2017/q1/52
- https://www.debian.org/security/2017/dsa-3773
- http://www.securitytracker.com/id/1037575
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2016-7056
- https://ftp.openbsd.org/pub/OpenBSD/patches/5.9/common/033_libcrypto.patch.sig
- https://ftp.openbsd.org/pub/OpenBSD/patches/6.0/common/016_libcrypto.patch.sig
- https://people.canonical.com/~ubuntu-security/cve/2016/CVE-2016-7056.html
- https://security-tracker.debian.org/tracker/CVE-2016-7056
