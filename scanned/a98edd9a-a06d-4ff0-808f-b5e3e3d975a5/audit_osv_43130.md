# [M] CVE-2026-72522

## Summary
Severity: Medium
Advisory: CVE-2026-72522
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72522
Type: osv

## Details
libexpat before 2.8.3 has an out-of-bounds read and resultant infinite loop because low surrogates are treated the same as high surrogates during Unicode processing in the *_toUtf16 functions.

## References
- http://www.openwall.com/lists/oss-security/2026/08/11/5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72522.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72522
- https://bugzilla.mozilla.org/show_bug.cgi?id=2053153
- https://github.com/libexpat/libexpat/pull/1296
