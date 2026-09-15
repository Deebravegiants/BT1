# [M] CVE-2022-34903

## Summary
Severity: Medium
Advisory: CVE-2022-34903
CVSS: 6.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2022-07-01
Source: https://osv.dev/vulnerability/CVE-2022-34903
Type: osv

## Details
GnuPG through 2.3.6, in unusual situations where an attacker possesses any secret-key information from a victim's keyring and other constraints (e.g., use of GPGME) are met, allows signature forgery via injection into the status line.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NPTAR76EIZY7NQFENSOZO7U473257OVZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VN63GBTMRWO36Y7BKA2WQHROAKCXKCBL/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VU64FUVG2PRZBSHFOQRSP7KDVEIZ23OS/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FRLWJQ76A4UKHI3Q36BKSJKS4LFLQO33/
- https://www.debian.org/security/2022/dsa-5174
- https://security.netapp.com/advisory/ntap-20220826-0005/
- https://bugs.debian.org/1014157
- https://dev.gnupg.org/T6027
- http://www.openwall.com/lists/oss-security/2022/07/02/1
- https://www.openwall.com/lists/oss-security/2022/06/30/1
