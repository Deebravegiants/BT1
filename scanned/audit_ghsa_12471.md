# [H] Buildkite Elastic CI for AWS symbolic link following vulnerability

## Summary
Severity: High
Advisory: GHSA-7c44-7j7v-w554
CVE: CVE-2023-43116
CWE: CWE-59
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-12-22
Source: https://github.com/advisories/GHSA-7c44-7j7v-w554
Type: github-advisory

## Affected
- Go: `github.com/buildkite/elastic-ci-stack-for-aws/v6` — affected >=0 <6.7.0

## Details
A symbolic link following vulnerability in Buildkite Elastic CI for AWS versions prior to 6.7.1 and 5.22.5 allows the buildkite-agent user to change ownership of arbitrary directories via the PIPELINE_PATH variable in the fix-buildkite-agent-builds-permissions script.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-43116
- https://github.com/buildkite/elastic-ci-stack-for-aws/commit/8f79882b6aa18fb8fc61f10c7047d2907b7a2f69
- https://github.com/atredispartners/advisories/blob/master/ATREDIS-2023-0003.md
- https://github.com/buildkite/elastic-ci-stack-for-aws
