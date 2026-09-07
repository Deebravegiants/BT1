# [M] tough failure to detect delegated target rollback

## Summary
Severity: Medium
Advisory: GHSA-q6r9-r9pw-4cf7
CVE: CVE-2025-2887
CWE: CWE-1025
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-28
Source: https://github.com/advisories/GHSA-q6r9-r9pw-4cf7
Type: github-advisory

## Affected
- crates.io: `tough` — affected >=0 <0.20.0

## Details
## Summary

When updating the snapshot role, TUF clients should ensure that any previously encountered targets or delegated targets metadata files continue to be present in new snapshot metadata files. Likewise, the new targets and delegated targets metadata versions must be greater than or equal to the previously encountered versions. While tough will perform this check for targets metadata files, it did not perform this check for delegated targets files.

## Impact

tough could fail to detect cases where delegated targets metadata was removed or rolled back to a previous version. As a result, tough could trust and download outdated targets that it should reject.

Impacted versions: < v0.20.0

## Patches

A fix for this issue is available in tough version 0.20.0 and later. Customers are advised to upgrade to version 0.20.0 or later and ensure any forked or derivative code is patched to incorporate the new fixes.

## Workarounds

There is no recommended work around. Customers are advised to upgrade to version 0.20.0 or the latest version.

## References

If you have any questions or comments about this advisory we ask that you contact AWS/Amazon Security via our vulnerability reporting page [1] or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.


[1] Vulnerability reporting page: [https://aws.amazon.com/security/vulnerability-reporting](https://aws.amazon.com/security/vulnerability-reporting%EF%BF%BC)

## Acknowledgement

These issues were identified by the [TUF-Conformance project](https://github.com/theupdateframework/tuf-conformance). We would like to thank Google for collaborating on this issue through the coordinated vulnerability disclosure process.

## References
- https://github.com/awslabs/tough/security/advisories/GHSA-q6r9-r9pw-4cf7
- https://nvd.nist.gov/vuln/detail/CVE-2025-2887
- https://github.com/awslabs/tough/commit/3345151a87c358d1ce43aeb7e8b3ebea5ebdbab4
- https://aws.amazon.com/security/security-bulletins/AWS-2025-007
- https://github.com/awslabs/tough
- https://github.com/awslabs/tough/releases/tag/tough-v0.20.0
