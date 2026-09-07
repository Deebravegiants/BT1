# [C] Command injection in ruby-git

## Summary
Severity: Critical
Advisory: GHSA-69p6-wvmq-27gg
CVE: CVE-2022-25648
CWE: CWE-88
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-20
Source: https://github.com/advisories/GHSA-69p6-wvmq-27gg
Type: github-advisory

## Affected
- RubyGems: `git` — affected >=0 <1.11.0

## Details
The package prior to v1.11.0 is vulnerable to Command Injection via git argument injection. When calling the `fetch(remote = 'origin', opts = {})` function, the remote parameter is passed to the `git fetch` subcommand in a way such that additional flags can be set. The additional flags can be used to perform a command injection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25648
- https://github.com/ruby-git/ruby-git/pull/569
- https://github.com/ruby-git/ruby-git/commit/291ca0946bec7164b90ad5c572ac147f512c7159
- https://github.com/ruby-git/ruby-git
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/git/CVE-2022-25648.yml
- https://lists.debian.org/debian-lts-announce/2023/01/msg00043.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PTJUF6SFPL4ZVSJQHGQ36KFPFO5DQVYZ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/Q2V3HOFU4ZVTQZHAVAVL3EX2KU53SP7R
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XWNJA7WPE67LJ3DJMWZ2TADHCZKWMY55
- https://snyk.io/vuln/SNYK-RUBY-GIT-2421270
