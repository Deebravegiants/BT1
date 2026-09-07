# [H] XSS Attack with Express API

## Summary
Severity: High
Advisory: GHSA-xrh7-m5pp-39r6
CVE: CVE-2023-23630
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2023-01-31
Source: https://github.com/advisories/GHSA-xrh7-m5pp-39r6
Type: github-advisory

## Affected
- npm: `eta` — affected >=0 <2.0.0

## Details
### Impact
XSS attack - anyone using the Express API is impacted

### Patches
The problem has been resolved. Users should upgrade to version 2.0.0.

### Workarounds
Don't pass user supplied data directly to `res.renderFile`. 

### References
_Are there any links users can visit to find out more?_
See https://github.com/eta-dev/eta/releases/tag/v2.0.0

## References
- https://github.com/eta-dev/eta/security/advisories/GHSA-xrh7-m5pp-39r6
- https://nvd.nist.gov/vuln/detail/CVE-2023-23630
- https://github.com/eta-dev/eta/commit/5651392462ee0ff19d77c8481081a99e5b9138dd
- https://github.com/eta-dev/eta
- https://github.com/eta-dev/eta/releases/tag/v2.0.0
