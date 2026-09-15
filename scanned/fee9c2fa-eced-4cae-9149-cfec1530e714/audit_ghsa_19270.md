# [M] OpenFGA Authorization Bypass

## Summary
Severity: Medium
Advisory: GHSA-c72g-53hw-82q7
CVE: CVE-2025-48371
CWE: CWE-285
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:N/VA:N/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2025-05-23
Source: https://github.com/advisories/GHSA-c72g-53hw-82q7
Type: github-advisory

## Affected
- Go: `github.com/openfga/openfga` — affected >=1.8.0 <1.8.13

## Details
### Overview
OpenFGA v1.8.0 to v1.8.12 ( openfga-0.2.16 <= Helm chart <= openfga-0.2.31, v1.8.0 <= docker <= v.1.8.12) are vulnerable to authorization bypass when certain Check and ListObject calls are executed.


### Am I Affected?
If you are using OpenFGA v1.8.0 to v1.8.12, specifically under the following conditions, you are affected by this authorization bypass vulnerability:
- Calling Check API or ListObjects with an [authorization model](https://openfga.dev/docs/concepts#what-is-an-authorization-model) that has a relationship directly assignable by both [type bound public access](https://openfga.dev/docs/concepts#what-is-type-bound-public-access) and [userset](https://openfga.dev/docs/modeling/building-blocks/usersets), and
- There are check or list object queries with [contextual tuples](https://openfga.dev/docs/interacting/contextual-tuples) for the relationship that can be directly assignable by both [type bound public access](https://openfga.dev/docs/concepts#what-is-type-bound-public-access) and [userset](https://openfga.dev/docs/modeling/building-blocks/usersets), and
- Those contextual tuples’s user field is an userset, and
- Type bound public access tuples are not assigned to the relationship

### Fix
Upgrade to v1.8.13. This upgrade is backwards compatible.

### Acknowledgments
OpenFGA would like to thank @udyvish for discovering this vulnerability.

## References
- https://github.com/openfga/openfga/security/advisories/GHSA-c72g-53hw-82q7
- https://nvd.nist.gov/vuln/detail/CVE-2025-48371
- https://github.com/openfga/openfga/commit/e5960d4eba92b723de8ff3a5346a07f50c1379ca
- https://github.com/openfga/openfga
- https://pkg.go.dev/vuln/GO-2025-3707
