# [C] ZDI-CAN-23894: Parse Server literalizeRegexPart SQL Injection Authentication Bypass Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-c2hr-cqg6-8j6r
CVE: CVE-2024-39309
CWE: CWE-288
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-07-01
Source: https://github.com/advisories/GHSA-c2hr-cqg6-8j6r
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=0 <6.5.7
- npm: `parse-server` — affected >=7.0.0 <7.1.0

## Details
### Impact

This vulnerability allows SQL injection when Parse Server is configured to use the PostgreSQL database.

### Patches

The algorithm to detect SQL injection has been improved.

### Workarounds

None.

### References

- https://github.com/parse-community/parse-server/security/advisories/GHSA-c2hr-cqg6-8j6r
- https://github.com/parse-community/parse-server/pull/9167 (fix for Parse Server 7)
- https://github.com/parse-community/parse-server/pull/9168 (fix for Parse Server 6)

### Credits

- Smile Thanapattheerakul of Trend Micro (finder)
- Manuel Trezza (coordinator)

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-c2hr-cqg6-8j6r
- https://nvd.nist.gov/vuln/detail/CVE-2024-39309
- https://github.com/parse-community/parse-server/pull/9167
- https://github.com/parse-community/parse-server/pull/9168
- https://github.com/parse-community/parse-server/commit/2edf1e4c0363af01e97a7fbc97694f851b7d1ff3
- https://github.com/parse-community/parse-server/commit/f332d54577608c5ad927255e06d8c694e2e0ff5b
- https://github.com/parse-community/parse-server
