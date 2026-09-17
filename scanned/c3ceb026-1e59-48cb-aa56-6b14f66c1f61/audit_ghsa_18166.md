# [H] @nubosoftware/node-static failure to catch exception can result in server crash

## Summary
Severity: High
Advisory: GHSA-27w5-gj5q-82fv
CVE: CVE-2025-11149
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-09-30
Source: https://github.com/advisories/GHSA-27w5-gj5q-82fv
Type: github-advisory

## Affected
- npm: `@nubosoftware/node-static` — affected >=0

## Details
This affects all versions of the package node-static; all versions of the package @nubosoftware/node-static. The package fails to catch an exception when user input includes null bytes. This allows attackers to access http://host/%00 and crash the server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-11149
- https://github.com/github/advisory-database/pull/6248
- https://github.com/cloudhead/node-static/commit/78879dc665f0f7137063794b6e0b6203a81c7f67
- https://github.com/cloudhead/node-static
- https://security.snyk.io/vuln/SNYK-JS-NODESTATIC-1297183
- https://security.snyk.io/vuln/SNYK-JS-NUBOSOFTWARENODESTATIC-3330728
