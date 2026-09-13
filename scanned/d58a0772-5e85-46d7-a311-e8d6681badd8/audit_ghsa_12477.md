# [H] Buildkite Elastic CI for AWS time-of-check-time-of-use race condition vulnerability

## Summary
Severity: High
Advisory: GHSA-r5hg-349q-mg2q
CVE: CVE-2023-43741
CWE: CWE-367
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-12-22
Source: https://github.com/advisories/GHSA-r5hg-349q-mg2q
Type: github-advisory

## Affected
- Go: `github.com/buildkite/elastic-ci-stack-for-aws/v6` — affected >=0 <6.7.1

## Details
A time-of-check-time-of-use race condition vulnerability in Buildkite Elastic CI for AWS versions prior to 6.7.1 and 5.22.5 allows the buildkite-agent user to bypass a symbolic link check for the PIPELINE_PATH variable in the fix-buildkite-agent-builds-permissions script.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-43741
- https://github.com/buildkite/elastic-ci-stack-for-aws/commit/edad0b158ea10a6647bb1c84629d93f5c3d8770e
- https://github.com/atredispartners/advisories/blob/master/ATREDIS-2023-0003.md
- https://github.com/buildkite/elastic-ci-stack-for-aws
