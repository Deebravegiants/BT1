# [M] tough terminating targets role delegations are not respected

## Summary
Severity: Medium
Advisory: GHSA-v4wr-j3w6-mxqc
CVE: CVE-2025-2886
CWE: CWE-670
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2025-03-28
Source: https://github.com/advisories/GHSA-v4wr-j3w6-mxqc
Type: github-advisory

## Affected
- crates.io: `tough` — affected >=0 <0.20.0

## Details
## Summary

Delegations are a mechanism defined by the TUF specification that allow multiple different identities to provide and sign content within a single repository. Terminating delegations and delegation priority give a TUF repository unambiguous control over how overlapping delegations are resolved. tough erroneously will not terminate a search as required, and will accept information from a lower-priority delegation that should have been ignored.

## Impact

When interacting with TUF repositories that use delegations, the tough client could fetch targets owned by the incorrect role. An actor which had delegated ownership of a subset of a TUF repository could provide arbitrary contents to tough clients for targets owned by the delegating identity.

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
- https://github.com/awslabs/tough/security/advisories/GHSA-v4wr-j3w6-mxqc
- https://nvd.nist.gov/vuln/detail/CVE-2025-2886
- https://github.com/awslabs/tough/commit/598111f88105a707ee68b0fa06c52da7176ea96a
- https://aws.amazon.com/security/security-bulletins/AWS-2025-007
- https://github.com/awslabs/tough
- https://github.com/awslabs/tough/releases/tag/tough-v0.20.0
