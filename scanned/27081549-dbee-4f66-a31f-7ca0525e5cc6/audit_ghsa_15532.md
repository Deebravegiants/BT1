# [H] basic-auth-connect's callback uses time unsafe string comparison

## Summary
Severity: High
Advisory: GHSA-7p89-p6hx-q4fw
CVE: CVE-2024-47178
CWE: CWE-208
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-09-30
Source: https://github.com/advisories/GHSA-7p89-p6hx-q4fw
Type: github-advisory

## Affected
- npm: `basic-auth-connect` — affected >=0 <1.1.0

## Details
### Impact

basic-auth-connect <1.1.0 uses a timing-unsafe equality comparison that can leak timing information

### Patches

this issue has been fixed in basic-auth-connect 1.1.0

### References

## References
- https://github.com/expressjs/basic-auth-connect/security/advisories/GHSA-7p89-p6hx-q4fw
- https://nvd.nist.gov/vuln/detail/CVE-2024-47178
- https://github.com/expressjs/basic-auth-connect/commit/bac1e6a8530e1efd0028800b9b588a37adb0d203
- https://github.com/expressjs/basic-auth-connect
