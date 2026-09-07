# [H] Cross site scripting in @awsui/components-react

## Summary
Severity: High
Advisory: GHSA-mf22-92pm-m8p8
CVE: CVE-2022-24709
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-25
Source: https://github.com/advisories/GHSA-mf22-92pm-m8p8
Type: github-advisory

## Affected
- npm: `@awsui/components-react` — affected >=0 <3.0.367

## Details
### Impact
Components could potentially allow cross-site scripting (XSS) in certain circumstances. These components could render content without adequate neutralization.

### Patches
Fixed in 3.0.367.

## References
- https://github.com/aws/awsui-documentation/security/advisories/GHSA-mf22-92pm-m8p8
- https://nvd.nist.gov/vuln/detail/CVE-2022-24709
- https://github.com/aws/awsui-documentation
- https://www.npmjs.com/package/@awsui/components-react
