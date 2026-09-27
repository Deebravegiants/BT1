# [H] pullit vulnerable to command injection

## Summary
Severity: High
Advisory: GHSA-8px5-63x9-5c7p
CVE: CVE-2018-25083
CWE: CWE-77
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-8px5-63x9-5c7p
Type: github-advisory

## Affected
- npm: `pullit` — affected >=0 <1.4.0

## Details
Versions of `pullit` prior to 1.4.0 are vulnerable to Command Injection. The package does not validate input on git branch names  and concatenates it to an exec call, allowing attackers to run arbitrary commands in the system.

## Recommendation

Upgrade to version 1.4.0 or later.

## Credits

This vulnerability was discovered by @lirantal

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-25083
- https://github.com/jkup/pullit/issues/23
- https://github.com/jkup/pullit/commit/4fec455774ee08f4dce0ef2ef934ffcc37219bfb
- https://hackerone.com/reports/315773
- https://github.com/jkup/pullit
- https://security.snyk.io/vuln/npm:pullit:20180214
