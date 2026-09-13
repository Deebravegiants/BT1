# [M] AWS CLI: Overly permissive File Permissions

## Summary
Severity: Medium
Advisory: GHSA-wfp6-f47h-hxc3
CVE: CVE-2026-13769
CWE: CWE-732
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-wfp6-f47h-hxc3
Type: github-advisory

## Affected
- PyPI: `awscli` — affected >=0 <1.44.78

## Details
### Summary
The AWS Command Line Interface (AWS CLI) is a unified tool for managing AWS services from the command line. Certain CLI subcommands wrote credential and configuration files with world-readable permissions on Unix-like systems with a default umask, allowing other local users on the same host to read credentials. 

### Impact
On Unix-like systems with a default umask, the following AWS CLI subcommands wrote credential or configuration files with world-readable permissions (0644) instead of owner-only (0600): 
- aws codeartifact login 

- aws iam create-virtual-mfa-device  

- aws deploy register 

Any other local user on the same host could read these files and obtain the credentials.  

Impacted versions: <=1.44.77 (v1) AND <=2.34.28 (v2)

### Patches
This issue has been addressed in AWS CLI v1 version 1.44.78 and AWS CLI v2 version 2.34.29. We recommend upgrading to the latest version and ensuring any forked or derivative code is patched to incorporate the new fixes. 

If you have any questions or comments about this advisory, we ask that you contact AWS Security via our vulnerability reporting page or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

## References
- https://github.com/aws/aws-cli/security/advisories/GHSA-wfp6-f47h-hxc3
- https://nvd.nist.gov/vuln/detail/CVE-2026-13769
- https://github.com/aws/aws-cli/pull/10191
- https://github.com/aws/aws-cli/pull/10194
- https://github.com/aws/aws-cli/pull/10206
- https://github.com/aws/aws-cli/commit/68811b5ad5cd74d06e944e073ee17bf889babf13
- https://github.com/aws/aws-cli/commit/84f0ec6afda03f8a26ff8dea403d02b1b31ee610
- https://github.com/aws/aws-cli/commit/e0799fde3c5e3138163e488e42bd3df7a0aa158f
- https://aws.amazon.com/security/security-bulletins/2026-049-aws
- https://github.com/aws/aws-cli
- https://github.com/aws/aws-cli/releases/tag/1.44.78
- https://github.com/aws/aws-cli/releases/tag/2.34.29
