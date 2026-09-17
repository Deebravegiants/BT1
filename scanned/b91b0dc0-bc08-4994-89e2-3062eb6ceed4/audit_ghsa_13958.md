# [M] @sideway/formula contains Regular Expression Denial of Service (ReDoS) Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-c2jc-4fpr-4vhg
CVE: CVE-2023-25166
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-02-08
Source: https://github.com/advisories/GHSA-c2jc-4fpr-4vhg
Type: github-advisory

## Affected
- npm: `@sideway/formula` — affected >=0 <3.0.1

## Details
### Impact

User-provided strings to formula's parser might lead to polynomial execution time.

### Patches

Users should upgrade to 3.0.1+.

### Workarounds

None.

## References
- https://github.com/hapijs/formula/security/advisories/GHSA-c2jc-4fpr-4vhg
- https://nvd.nist.gov/vuln/detail/CVE-2023-25166
- https://github.com/hapijs/formula/commit/9fbc20a02d75ae809c37a610a57802cd1b41b3fe
- https://github.com/hapijs/formula
