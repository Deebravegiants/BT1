# [C] OS Command Injection in strong-nginx-controller

## Summary
Severity: Critical
Advisory: GHSA-4v9w-pvwr-38h3
CVE: CVE-2020-7621
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-4v9w-pvwr-38h3
Type: github-advisory

## Affected
- npm: `strong-nginx-controller` — affected >=0

## Details
strong-nginx-controller through 1.0.2 is vulnerable to Command Injection. It allows execution of arbitrary command as part of the '_nginxCmd()' function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7621
- https://github.com/strongloop/strong-nginx-controller/blob/master/lib/server.js#L65
- https://snyk.io/vuln/SNYK-JS-STRONGNGINXCONTROLLER-564248
