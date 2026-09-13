# [H] Cloudinary Node SDK is vulnerable to Arbitrary Argument Injection through parameters that include an ampersand

## Summary
Severity: High
Advisory: GHSA-g4mf-96x5-5m2c
CVE: CVE-2025-12613
CWE: CWE-88
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2025-11-10
Source: https://github.com/advisories/GHSA-g4mf-96x5-5m2c
Type: github-advisory

## Affected
- npm: `cloudinary` — affected >=0 <2.7.0

## Details
Versions of the package cloudinary before 2.7.0 are vulnerable to Arbitrary Argument Injection due to improper parsing of parameter values containing an ampersand. An attacker can inject additional, unintended parameters. This could lead to a variety of malicious outcomes, such as bypassing security checks, altering data, or manipulating the application's behavior.

**Note:**
Following our established security policy, we attempted to contact the maintainer regarding this vulnerability, but haven't received a response.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-12613
- https://github.com/cloudinary/cloudinary_npm/pull/709
- https://github.com/cloudinary/cloudinary_npm/commit/ec4b65f2b3461365c569198ed6d2cfa61cca4050
- https://github.com/cloudinary/cloudinary_npm
- https://security.snyk.io/vuln/SNYK-JS-CLOUDINARY-10495740
