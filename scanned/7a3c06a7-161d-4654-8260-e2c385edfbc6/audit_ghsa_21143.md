# [C] OS Command Injection in awesome spawn

## Summary
Severity: Critical
Advisory: GHSA-qpqw-mc85-qvm9
CVE: CVE-2014-0156
CWE: CWE-78
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-01
Source: https://github.com/advisories/GHSA-qpqw-mc85-qvm9
Type: github-advisory

## Affected
- RubyGems: `awesome_spawn` — affected >=0 <1.2.0

## Details
Awesome spawn prior to version 1.2.0 contains OS command injection vulnerability, which allows execution of additional commands passed to Awesome spawn as arguments. If untrusted input was included in command arguments, attacker could use this flaw to execute arbitrary command.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-0156
- https://github.com/ManageIQ/awesome_spawn/commit/e524f85f1c6e292ef7d117d7818521307ac269ff
- https://github.com/ManageIQ/awesome_spawn
- https://rubysec.com/advisories/CVE-2014-0156
