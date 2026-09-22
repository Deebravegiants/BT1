# [M] Untrusted data fed into `Data.init(base32Encoded:)` can result in exposing server memory and/or crash

## Summary
Severity: Medium
Advisory: GHSA-pqwh-c2f3-vxmq
CVE: CVE-2021-32742
CWE: CWE-502
Ecosystem: SwiftURL
Published: 2023-06-09
Source: https://github.com/advisories/GHSA-pqwh-c2f3-vxmq
Type: github-advisory

## Affected
- SwiftURL: `github.com/vapor/vapor` — affected >=0 <4.47.2

## Details
### Impact
A bug in the `Data.init(base32Encoded:)` function opens up the potential for exposing server memory and/or crashing the server (Denial of Service) for applications where untrusted data can end up in said function. Vapor does not currently use this function itself so this only impact applications that use the impacted function directly or through other dependencies.

### Patches
This issue has been patched in 4.47.2.

### Workarounds
Use an alternative to Vapor's built-in `Data.init(base32Encoded:)`.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Vapor](https://github.com/vapor/vapor)
* Ask in [Discord](http://vapor.team)

## References
- https://github.com/vapor/vapor/security/advisories/GHSA-pqwh-c2f3-vxmq
- https://nvd.nist.gov/vuln/detail/CVE-2021-32742
- https://github.com/vapor/vapor
- https://github.com/vapor/vapor/releases/tag/4.47.2
