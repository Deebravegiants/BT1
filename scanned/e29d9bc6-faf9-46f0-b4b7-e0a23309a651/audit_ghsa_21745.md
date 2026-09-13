# [M] Gitea Exposes Private Email Addresses

## Summary
Severity: Medium
Advisory: GHSA-f5fj-7265-jxhj
CVE: CVE-2018-1000803
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-f5fj-7265-jxhj
Type: github-advisory

## Affected
- Go: `github.com/go-gitea/gitea` — affected >=0 <1.5.1

## Details
Gitea version prior to version 1.5.1 contains a CWE-200 vulnerability that can result in Exposure of users private email addresses. This attack appear to be exploitable via Watch a repository to receive email notifications. Emails received contain the other recipients even if they have the email set as private. This vulnerability appears to have been fixed in 1.5.1.

### Specific Go Packages Affected
github.com/go-gitea/gitea/models

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000803
- https://github.com/go-gitea/gitea/pull/4664
- https://github.com/go-gitea/gitea/pull/4664/files#diff-146e0c2b5bb1ea96c9fb73d509456e57
- https://github.com/go-gitea/gitea/commit/194a11eb110cd98fc2ba52861abf7770db6885a3
