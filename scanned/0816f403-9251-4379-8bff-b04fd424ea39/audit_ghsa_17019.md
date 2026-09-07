# [C] Server crashes on invalid Cloud Function or Cloud Job name

## Summary
Severity: Critical
Advisory: GHSA-6hh7-46r2-vf29
CVE: CVE-2024-29027
CWE: CWE-20, CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-03-19
Source: https://github.com/advisories/GHSA-6hh7-46r2-vf29
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=0 <6.5.5
- npm: `parse-server` — affected >=7.0.0-alpha.1 <7.0.0-alpha.29

## Details
### Impact

Calling an invalid Parse Server Cloud Function name or Cloud Job name crashes server and may allow for code injection.

### Patches

Added string sanitation for Cloud Function name and Cloud Job name.

### Workarounds

Sanitize the Cloud Function name and Cloud Job name before it reaches Parse Server.

### References

- https://github.com/parse-community/parse-server/security/advisories/GHSA-6hh7-46r2-vf29
- https://github.com/parse-community/parse-server/releases/tag/7.0.0-alpha.29 (Fix for Parse Server 7 alpha)
- https://github.com/parse-community/parse-server/releases/tag/6.5.5 (Fix for Parse Server 6 LTS)

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-6hh7-46r2-vf29
- https://nvd.nist.gov/vuln/detail/CVE-2024-29027
- https://github.com/parse-community/parse-server/commit/5ae6d6a36d75c4511029f0ba5673ae4b2999179b
- https://github.com/parse-community/parse-server/commit/9f6e3429d3b326cf4e2994733c618d08032fac6e
- https://github.com/parse-community/parse-server
- https://github.com/parse-community/parse-server/releases/tag/6.5.5
- https://github.com/parse-community/parse-server/releases/tag/7.0.0-alpha.29
