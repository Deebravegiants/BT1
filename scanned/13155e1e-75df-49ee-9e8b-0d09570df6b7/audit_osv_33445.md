# [C] CryptX for Perl before version 0.065 contains a dependency that may be susceptible to malformed unicode

## Summary
Severity: Critical
Advisory: CVE-2025-40912
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-11
Source: https://osv.dev/vulnerability/CVE-2025-40912
Type: osv

## Details
CryptX for Perl before version 0.065 contains a dependency that may be susceptible to malformed unicode.

CryptX embeds the tomcrypt library. The versions of that library in CryptX before 0.065 may be susceptible to CVE-2019-17362.

## References
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40912.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40912
- https://github.com/libtom/libtomcrypt/issues/507
- https://github.com/DCIT/perl-CryptX
