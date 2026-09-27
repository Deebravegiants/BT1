# [H] OS Command Injection in pixl-class

## Summary
Severity: High
Advisory: GHSA-vm5j-vqr6-v7v8
CVE: CVE-2020-7640
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-12-10
Source: https://github.com/advisories/GHSA-vm5j-vqr6-v7v8
Type: github-advisory

## Affected
- npm: `pixl-class` — affected >=0 <1.0.3

## Details
pixl-class prior to 1.0.3 allows execution of arbitrary commands. The members argument of the create function can be controlled by users without any sanitization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7640
- https://github.com/jhuckaby/pixl-class/commit/47677a3638e3583e42f3a05cc7f0b30293d2acc8
- https://github.com/jhuckaby/pixl-class/commit/47677a3638e3583e42f3a05cc7f0b30293d2acc8,
- https://snyk.io/vuln/SNYK-JS-PIXLCLASS-564968
