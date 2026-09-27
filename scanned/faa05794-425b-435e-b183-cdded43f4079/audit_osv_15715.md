# [H] CVE-2019-19022

## Summary
Severity: High
Advisory: CVE-2019-19022
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-11-17
Source: https://osv.dev/vulnerability/CVE-2019-19022
Type: osv

## Details
iTerm2 through 3.3.6 has potentially insufficient documentation about the presence of search history in com.googlecode.iterm2.plist, which might allow remote attackers to obtain sensitive information, as demonstrated by searching for the NoSyncSearchHistory string in .plist files within public Git repositories.

## References
- https://gitlab.com/gnachman/iterm2/issues/8491
