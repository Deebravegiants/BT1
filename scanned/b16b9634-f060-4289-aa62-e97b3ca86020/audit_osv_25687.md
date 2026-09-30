# [M] Late-Unicode normalization vulnerability in SHIRASAGI

## Summary
Severity: Medium
Advisory: CVE-2023-41889
Aliases: GHSA-xr45-c2jv-2v9r
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2023-09-15
Source: https://osv.dev/vulnerability/CVE-2023-41889
Type: osv

## Details
SHIRASAGI is a Content Management System. Prior to version 1.18.0, SHIRASAGI is vulnerable to a Post-Unicode normalization issue. This happens when a logical validation or a security check is performed before a Unicode normalization. The Unicode character equivalent of a character would resurface after the normalization. The fix is initially performing the Unicode normalization and then strip for all whitespaces and then checking for a blank string. This issue has been fixed in version 1.18.0.

## References
- https://github.com/shirasagi/shirasagi/blob/f249ce3f06f6bfbc0017b38f5c13de424334c3ea/app/models/concerns/rdf/object.rb#L68-L72
- https://sim4n6.beehiiv.com/p/unicode-characters-bypass-security-checks
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/41xxx/CVE-2023-41889.json
- https://github.com/shirasagi/shirasagi/security/advisories/GHSA-xr45-c2jv-2v9r
- https://nvd.nist.gov/vuln/detail/CVE-2023-41889
