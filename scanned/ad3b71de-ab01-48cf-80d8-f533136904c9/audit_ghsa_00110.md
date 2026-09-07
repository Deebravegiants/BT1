# [C] Git-fastclone passes user modifiable strings directly to a shell command

## Summary
Severity: Critical
Advisory: GHSA-mf6w-45cf-qhmp
CVE: CVE-2015-8969
CWE: CWE-77
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-08-15
Source: https://github.com/advisories/GHSA-mf6w-45cf-qhmp
Type: github-advisory

## Affected
- RubyGems: `git-fastclone` — affected >=0 <1.0.5

## Details
git-fastclone before 1.0.5 passes user modifiable strings directly to a shell command. An attacker can execute malicious commands by modifying the strings that are passed as arguments to `cd ` and `git clone ` commands in the library.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-8969
- https://github.com/square/git-fastclone/pull/5
- https://hackerone.com/reports/105190
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/git-fastclone/CVE-2015-8969.yml
- https://github.com/square/git-fastclone
- https://web.archive.org/web/20161108132238/http://www.securityfocus.com/bid/81433
