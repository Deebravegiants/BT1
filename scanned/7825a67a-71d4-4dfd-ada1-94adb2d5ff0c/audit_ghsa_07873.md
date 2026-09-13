# [M] AWS CLI: cli_history database does not restrict file permissions on Unix systems

## Summary
Severity: Medium
Advisory: GHSA-747p-wmpv-9c78
CWE: CWE-276
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-02-27
Source: https://github.com/advisories/GHSA-747p-wmpv-9c78
Type: github-advisory

## Affected
- PyPI: `awscli` — affected >=1.13.0 <1.44.38

## Details
**Summary**
AWS CLI is a command line tool for interacting with AWS services. When the cli_history feature is enabled, the history database file is created with default permissions, potentially allowing other local users on a multi-user system to read the file.

**Impact**
When cli_history is enabled, AWS CLI stores command history including command parameters and API request/response data in a local SQLite database. On multi-user Unix systems, the default file permissions may allow other local users to read this file, potentially exposing sensitive information. This issue only affects users who have explicitly enabled cli_history, which is disabled by default.

**Impacted versions:** 1.13.0 - 1.44.37 (v1), 2.0.0 - 2.33.20 (v2)

**Patches**
This issue has been addressed in the latest versions 2.33.21 and 1.44.38 of AWS CLI. We recommend upgrading to the latest version and ensuring any forked or derivative code is patched to incorporate the new fixes. 

**Workarounds**
Users can manually set restrictive permissions on the history database file. Alternatively, disable cli_history by removing `cli_history = enabled` from the AWS config file.

**Resources**
If there are any questions or comments about this advisory, contact AWS Security via the [vulnerability reporting page](https://aws.amazon.com/security/vulnerability-reporting) or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

## References
- https://github.com/aws/aws-cli/security/advisories/GHSA-747p-wmpv-9c78
- https://github.com/aws/aws-cli
