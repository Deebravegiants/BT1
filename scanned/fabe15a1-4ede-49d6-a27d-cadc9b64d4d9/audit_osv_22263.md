# [H] Buffer overflow in pjsip

## Summary
Severity: High
Advisory: CVE-2022-24754
Aliases: GHSA-73f7-48m9-w662
CVSS: 8.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-03-11
Source: https://osv.dev/vulnerability/CVE-2022-24754
Type: osv

## Details
PJSIP is a free and open source multimedia communication library written in C language. In versions prior to and including 2.12 PJSIP there is a stack-buffer overflow vulnerability which only impacts PJSIP users who accept hashed digest credentials (credentials with data_type `PJSIP_CRED_DATA_DIGEST`). This issue has been patched in the master branch of the PJSIP repository and will be included with the next release. Users unable to upgrade need to check that the hashed digest data length must be equal to `PJSIP_MD5STRLEN` before passing to PJSIP.

## References
- https://lists.debian.org/debian-lts-announce/2024/09/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24754.json
- https://github.com/pjsip/pjproject/security/advisories/GHSA-73f7-48m9-w662
- https://nvd.nist.gov/vuln/detail/CVE-2022-24754
- https://security.gentoo.org/glsa/202210-37
- https://github.com/pjsip/pjproject/commit/d27f79da11df7bc8bb56c2f291d71e54df8d2c47
- https://lists.debian.org/debian-lts-announce/2022/03/msg00035.html
- https://lists.debian.org/debian-lts-announce/2023/08/msg00038.html
