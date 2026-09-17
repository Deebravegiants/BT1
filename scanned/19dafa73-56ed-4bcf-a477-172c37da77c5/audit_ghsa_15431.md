# [H] unzip-stream allows Arbitrary File Write via artifact extraction

## Summary
Severity: High
Advisory: GHSA-6jrj-vc65-c983
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-08-26
Source: https://github.com/advisories/GHSA-6jrj-vc65-c983
Type: github-advisory

## Affected
- npm: `unzip-stream` — affected >=0 <0.3.2

## Details
### Impact

When using the `Extract()` method of unzip-stream, malicious zip files were able to write to paths they shouldn't be allowed to.

### Patches

Fixed in 0.3.2

### References

- https://snyk.io/research/zip-slip-vulnerability
- https://github.com/mhr3/unzip-stream/compare/v0.3.1...v0.3.2

### Credits

Justin Taft from Google

## References
- https://github.com/mhr3/unzip-stream/security/advisories/GHSA-6jrj-vc65-c983
- https://github.com/mhr3/unzip-stream/commit/ab67989719abb4dcc774d02de266151905b8d45a
- https://github.com/mhr3/unzip-stream
- https://github.com/mhr3/unzip-stream/compare/v0.3.1...v0.3.2
- https://snyk.io/research/zip-slip-vulnerability
