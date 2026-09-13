# [C] ejs template injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-phwq-j96m-2c2q
CVE: CVE-2022-29078
CWE: CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-26
Source: https://github.com/advisories/GHSA-phwq-j96m-2c2q
Type: github-advisory

## Affected
- npm: `ejs` — affected >=0 <3.1.7

## Details
The ejs (aka Embedded JavaScript templates) package 3.1.6 for Node.js allows server-side template injection in settings[view options][outputFunctionName]. This is parsed as an internal option, and overwrites the outputFunctionName option with an arbitrary OS command (which is executed upon template compilation).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-29078
- https://github.com/mde/ejs/commit/15ee698583c98dadc456639d6245580d17a24baf
- https://eslam.io/posts/ejs-server-side-template-injection-rce
- https://github.com/mde/ejs
- https://github.com/mde/ejs/releases
- https://security.netapp.com/advisory/ntap-20220804-0001
