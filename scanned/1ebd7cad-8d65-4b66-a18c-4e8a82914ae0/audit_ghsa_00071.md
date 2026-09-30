# [H] git-fastclone permits arbitrary shell command execution from .gitmodules

## Summary
Severity: High
Advisory: GHSA-8gg6-3r63-25m8
CVE: CVE-2015-8968
CWE: CWE-77
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-08-15
Source: https://github.com/advisories/GHSA-8gg6-3r63-25m8
Type: github-advisory

## Affected
- RubyGems: `git-fastclone` — affected >=0 <1.0.1

## Details
git-fastclone before 1.0.1 permits arbitrary shell command execution from .gitmodules. If an attacker can instruct a user to run a recursive clone from a repository they control, they can get a client to run an arbitrary shell command. Alternately, if an attacker can MITM an unencrypted git clone, they could exploit this. The ext command will be run if the repository is recursively cloned or if submodules are updated. This attack works when cloning both local and remote repositories.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-8968
- https://github.com/square/git-fastclone/pull/2
- https://hackerone.com/reports/104465
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/git-fastclone/CVE-2015-8968.yml
- https://github.com/square/git-fastclone
- https://web.archive.org/web/20200227213019/http://www.securityfocus.com/bid/81433
