# [M] CVE-2021-41250

## Summary
Severity: Medium
Advisory: CVE-2021-41250
Aliases: GHSA-j8c3-8x46-8pp6
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2021-11-05
Source: https://osv.dev/vulnerability/CVE-2021-41250
Type: osv

## Details
Python discord bot is the community bot for the Python Discord community. In affected versions when a non-blacklisted URL and an otherwise triggering filter token is included in the same message the token filter does not trigger. This means that by including any non-blacklisted URL moderation filters can be bypassed. This issue has been resolved in commit 67390298852513d13e0213870e50fb3cff1424e0

## References
- https://github.com/python-discord/bot/commit/67390298852513d13e0213870e50fb3cff1424e0
- https://github.com/python-discord/bot/security/advisories/GHSA-j8c3-8x46-8pp6
