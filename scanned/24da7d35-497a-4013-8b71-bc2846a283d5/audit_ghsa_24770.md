# [M] GitLab Grit Gem for Ruby contains a flaw allowing arbitrary commands to be executed

## Summary
Severity: Medium
Advisory: GHSA-95xq-v4m2-fq3r
CVE: CVE-2013-4489
CWE: CWE-20
Ecosystem: RubyGems
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-95xq-v4m2-fq3r
Type: github-advisory

## Affected
- RubyGems: `gitlab-grit` — affected >=0 <2.6.1

## Details
The Grit gem for Ruby, as used in GitLab 5.2 before 5.4.1 and 6.x before 6.2.3, allows remote authenticated users to execute arbitrary commands, as demonstrated by the search box for the GitLab code search feature.

GitLab Grit Gem for Ruby contains a flaw in the app/contexts/search_context.rb script. The issue is triggered when input passed via the code search box is not properly sanitized, which allows strings to be evaluated by the shell. This may allow a remote attacker to execute arbitrary commands.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4489
- https://github.com/gitlabhq/grit/commit/40f33a4f4f5604c2a531a1d86901fd81ac4402c4
- https://github.com/gitlabhq/grit
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/gitlab-grit/CVE-2013-4489.yml
- https://gitlab.com/gitlab-org/gitlab-grit/-/blob/v2.6.1/History.txt?ref_type=tags#L2
- https://www.gitlab.com/2013/11/04/gitlab-ce-6-2-and-5-4-security-release
