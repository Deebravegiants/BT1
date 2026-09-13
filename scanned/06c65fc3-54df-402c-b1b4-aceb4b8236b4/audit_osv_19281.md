# [H] CVE-2020-9708

## Summary
Severity: High
Advisory: CVE-2020-9708
Aliases: GHSA-cgj4-x2hh-2x93
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-08-14
Source: https://osv.dev/vulnerability/CVE-2020-9708
Type: osv

## Details
The resolveRepositoryPath function doesn't properly validate user input and a malicious user may traverse to any valid Git repository outside the repoRoot. This issue may lead to unauthorized access of private Git repositories as long as the malicious user knows or brute-forces the location of the repository.

## References
- https://github.com/adobe/git-server/security/advisories/GHSA-cgj4-x2hh-2x93
