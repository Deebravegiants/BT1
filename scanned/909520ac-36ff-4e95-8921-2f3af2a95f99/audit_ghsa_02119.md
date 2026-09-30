# [H] Regular Expression Denial of Service in jquery-validation

## Summary
Severity: High
Advisory: GHSA-jxwx-85vp-gvwm
CVE: CVE-2021-21252
CWE: CWE-400
Ecosystem: NuGet, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-01-13
Source: https://github.com/advisories/GHSA-jxwx-85vp-gvwm
Type: github-advisory

## Affected
- npm: `jquery-validation` — affected >=0 <1.19.3
- NuGet: `jQuery.Validation` — affected >=0 <1.19.3

## Details
The GitHub Security Lab team has identified potential security vulnerabilities in jquery.validation.

The project contains one or more regular expressions that are vulnerable to ReDoS (Regular Expression Denial of Service)

This issue was discovered and reported by GitHub team member @erik-krogh (Erik Krogh Kristensen).

## References
- https://github.com/jquery-validation/jquery-validation/security/advisories/GHSA-jxwx-85vp-gvwm
- https://nvd.nist.gov/vuln/detail/CVE-2021-21252
- https://github.com/jquery-validation/jquery-validation/pull/2371
- https://github.com/jquery-validation/jquery-validation/commit/5d8f29eef363d043a8fec4eb86d42cadb5fa5f7d
- https://github.com/jquery-validation/jquery-validation
- https://jqueryvalidation.org/#installation-via-package-managers
- https://lists.debian.org/debian-lts-announce/2023/08/msg00040.html
- https://security.netapp.com/advisory/ntap-20210219-0005
- https://securitylab.github.com/advisories/GHSL-2020-294-redos-jquery-validation
- https://www.npmjs.com/package/jquery-validation
- https://www.nuget.org/packages/jquery.validation
