# [H] ruby-git has potential remote code execution vulnerability

## Summary
Severity: High
Advisory: GHSA-pfpr-3463-c6jh
CVE: CVE-2022-46648
CWE: CWE-94
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-09
Source: https://github.com/advisories/GHSA-pfpr-3463-c6jh
Type: github-advisory

## Affected
- RubyGems: `git` — affected >=1.2.0 <1.13.0

## Details
The git gem, between versions 1.2.0 and 1.12.0, incorrectly parsed the output of the `git ls-files` command using `eval()` to unescape quoted file names. If a file name was added to the git repository contained special characters, such as `\n`, then the `git ls-files` command would print the file name in quotes and escape any special characters. If the `Git#ls_files` method encountered a quoted file name it would use `eval()` to unquote and unescape any special characters, leading to potential remote code execution. Version 1.13.0 of the git gem was released which correctly parses any quoted file names.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-46648
- https://github.com/ruby-git/ruby-git/pull/602
- https://github.com/ruby-git/ruby-git
- https://github.com/ruby-git/ruby-git/releases/tag/v1.13.0
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/git/CVE-2022-46648.yml
- https://jvn.jp/en/jp/JVN16765254/index.html
- https://lists.debian.org/debian-lts-announce/2023/01/msg00043.html
