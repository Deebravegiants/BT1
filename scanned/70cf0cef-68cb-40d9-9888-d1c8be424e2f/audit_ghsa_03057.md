# [H] Arbitrary Code Execution in grunt

## Summary
Severity: High
Advisory: GHSA-m5pj-vjjf-4m3h
CVE: CVE-2020-7729
CWE: CWE-1188
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-m5pj-vjjf-4m3h
Type: github-advisory

## Affected
- npm: `grunt` — affected >=0 <1.3.0

## Details
The package grunt before 1.3.0 are vulnerable to Arbitrary Code Execution due to the default usage of the function load() instead of its secure replacement safeLoad() of the package js-yaml inside grunt.file.readYAML.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7729
- https://github.com/gruntjs/grunt/commit/e350cea1724eb3476464561a380fb6a64e61e4e7
- https://github.com/gruntjs/grunt/blob/master/lib/grunt/file.js%23L249
- https://lists.debian.org/debian-lts-announce/2020/09/msg00008.html
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-607922
- https://snyk.io/vuln/SNYK-JS-GRUNT-597546
- https://usn.ubuntu.com/4595-1
