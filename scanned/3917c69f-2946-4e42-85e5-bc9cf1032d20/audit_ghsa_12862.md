# [C] global-modules-path Command Injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-vvj3-85vf-fgmw
CVE: CVE-2022-21191
CWE: CWE-77, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-13
Source: https://github.com/advisories/GHSA-vvj3-85vf-fgmw
Type: github-advisory

## Affected
- npm: `global-modules-path` — affected >=0 <3.0.0

## Details
Versions of the package global-modules-path before 3.0.0 are vulnerable to Command Injection due to missing input sanitization or other checks and sandboxes being employed to the getPath function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-21191
- https://github.com/rosen-vladimirov/global-modules-path/commit/edbdaff077ea0cf295b1469923c06bbccad3c180
- https://github.com/lorenzomigliorero/npm-node-utils/blob/b55dd81c597db657c9751332bb2242403fd3e26b/index.js%23L186
- https://github.com/rosen-vladimirov/global-modules-path
- https://github.com/rosen-vladimirov/global-modules-path/releases/tag/v3.0.0
- https://security.snyk.io/vuln/SNYK-JS-GLOBALMODULESPATH-3167973
