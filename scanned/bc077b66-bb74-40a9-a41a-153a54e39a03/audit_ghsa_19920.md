# [M] tough root metadata version is not checked for sequential versioning

## Summary
Severity: Medium
Advisory: GHSA-5vmp-m5v2-hx47
CVE: CVE-2025-2885
CWE: CWE-1288
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2025-03-28
Source: https://github.com/advisories/GHSA-5vmp-m5v2-hx47
Type: github-advisory

## Affected
- crates.io: `tough` — affected >=0 <0.20.0

## Details
## Summary

When updating the root role, a TUF client must establish a trusted line of continuity to the latest set of keys. While sequentially downloading new versions of the root metadata file, tough will not check that the root object version it received was the next sequential version from the previously trusted root metadata.

## Impact

The tough client will trust an outdated or rotated root role in the event that an actor with control of the storage medium of a trusted TUF repository inappropriately replaced the contents of one of the root metadata files with an adequately signed previous version. As a result, tough could trust content associated with a previous root role.

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
- https://github.com/awslabs/tough/security/advisories/GHSA-5vmp-m5v2-hx47
- https://nvd.nist.gov/vuln/detail/CVE-2025-2885
- https://github.com/awslabs/tough/commit/0eeb60aefe27f00b65730634b788a1aafb8bf3c6
- https://aws.amazon.com/security/security-bulletins/AWS-2025-007
- https://github.com/awslabs/tough
- https://github.com/awslabs/tough/releases/tag/tough-v0.20.0
