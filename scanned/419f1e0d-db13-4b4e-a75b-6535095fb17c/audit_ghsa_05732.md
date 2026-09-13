# [M] lakeFS is Missing Timestamp Validation in S3 Gateway Authentication

## Summary
Severity: Medium
Advisory: GHSA-f2ph-gc9m-q55f
CVE: CVE-2025-68671
CWE: CWE-294
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-01-15
Source: https://github.com/advisories/GHSA-f2ph-gc9m-q55f
Type: github-advisory

## Affected
- Go: `github.com/treeverse/lakefs` — affected >=0 <1.75.0

## Details
### Impact
LakeFS's S3 gateway does not validate timestamps in authenticated requests, allowing replay attacks. An attacker who captures a valid signed request (e.g., through network interception, logs, or compromised systems) can replay that request until credentials are rotated, even after the request is intended to expire.

### Patches
This issue affects all versions of lakeFS up to and including v1.74.4.

The vulnerability has been fixed in version v1.75.0.

Users should upgrade to version v1.75.0.

### Workarounds

Until upgraded, implement these mitigations:

- **Use short-lived credentials** - Rotate access keys frequently and **deactivate old keys**. For regular requests, captured requests only work until rotation. For presigned URLs, they remain valid until the credentials used to create them are deactivated.
- **Network controls** - Restrict S3 gateway access to trusted networks/IPs to limit where replay attacks can originate.

Note: These workarounds reduce risk but do not fully eliminate the vulnerability.

### References
- Original issue: https://github.com/treeverse/lakeFS/issues/9599
- AWS Signature V4 Documentation: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_sigv.html
- AWS Signature V4 S3 Requests: https://docs.aws.amazon.com/AmazonS3/latest/API/sig-v4-authenticating-requests.html
- AWS Signature V2 Documentation: https://docs.aws.amazon.com/AmazonS3/latest/API/sig-v4-header-based-auth.html

## References
- https://github.com/treeverse/lakeFS/security/advisories/GHSA-f2ph-gc9m-q55f
- https://nvd.nist.gov/vuln/detail/CVE-2025-68671
- https://github.com/treeverse/lakeFS/issues/9599
- https://github.com/treeverse/lakeFS/pull/9710
- https://github.com/treeverse/lakeFS/commit/92966ae611d7f1a2bbe7fd56f9568c975aab2bd8
- https://github.com/treeverse/lakeFS
