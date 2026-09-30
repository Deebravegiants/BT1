# [C] Growl before 1.10.0 vulnerable to Command Injection

## Summary
Severity: Critical
Advisory: GHSA-qh2h-chj9-jffq
CVE: CVE-2017-16042
CWE: CWE-78, CWE-94
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-06-08
Source: https://github.com/advisories/GHSA-qh2h-chj9-jffq
Type: github-advisory

## Affected
- npm: `growl` — affected >=0 <1.10.0

## Details
Affected versions of `growl` do not properly sanitize input prior to passing it into a shell command, allowing for arbitrary command execution.


## Recommendation

Update to version 1.10.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16042
- https://github.com/tj/node-growl/issues/60
- https://github.com/tj/node-growl/pull/61
- https://github.com/tj/node-growl/pull/62
- https://github.com/tj/node-growl/commit/d71177d5331c9de4658aca62e0ac921f178b0669
- https://github.com/tj/node-growl
- https://www.npmjs.com/advisories/146
