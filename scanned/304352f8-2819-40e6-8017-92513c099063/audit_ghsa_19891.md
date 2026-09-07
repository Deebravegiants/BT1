# [M] tough timestamp metadata is cached when it fails snapshot rollback check

## Summary
Severity: Medium
Advisory: GHSA-76g3-38jv-wxh4
CVE: CVE-2025-2888
CWE: CWE-1025
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-28
Source: https://github.com/advisories/GHSA-76g3-38jv-wxh4
Type: github-advisory

## Affected
- crates.io: `tough` — affected >=0 <0.20.0

## Details
## Summary

TUF repositories use the timestamp role to protect against rollback events by enabling an automated process to periodically sign the role's metadata. While tough will ensure that the version of snapshot metadata in new timestamp metadata files was always greater than or equal to the previously trusted version, it will only do so after persisting the timestamp metadata to its cache.

## Impact

If the tough client successfully detects a rollback event in which timestamp metadata contains outdated snapshot metadata, the invalid timestamp metadata will still be persisted to cache as trusted. tough may then subsequently incorrectly identify valid timestamp metadata as being rolled back, preventing the client from consuming valid updates.

Impacted versions: < v0.20.0

## Patches

A fix for this issue is available in tough version 0.20.0 and later. Customers are advised to upgrade to version 0.20.0 or later and ensure any forked or derivative code is patched to incorporate the new fixes.

## Workarounds

There is no recommended work around. Customers are advised to upgrade to version 0.20.0 or the latest version.

## References

If you have any questions or comments about this advisory we ask that you contact AWS/Amazon Security via our vulnerability reporting page [1] or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.


[1] Vulnerability reporting page: https://aws.amazon.com/security/vulnerability-reporting

## Acknowledgement

These issues were identified by the [TUF-Conformance project](https://github.com/theupdateframework/tuf-conformance). We would like to thank Google for collaborating on this issue through the coordinated vulnerability disclosure process.

## References
- https://github.com/awslabs/tough/security/advisories/GHSA-76g3-38jv-wxh4
- https://nvd.nist.gov/vuln/detail/CVE-2025-2888
- https://github.com/awslabs/tough/commit/9b400e1c8b7d6b9ab8009104fa7fe5884db05f18
- https://aws.amazon.com/security/security-bulletins/AWS-2025-007
- https://github.com/awslabs/tough
- https://github.com/awslabs/tough/releases/tag/tough-v0.20.0
