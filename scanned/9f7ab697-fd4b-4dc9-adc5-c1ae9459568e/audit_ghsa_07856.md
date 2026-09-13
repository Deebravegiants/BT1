# [M] OpenFGA Improper Policy Enforcement

## Summary
Severity: Medium
Advisory: GHSA-jq9f-gm9w-rwm9
CVE: CVE-2026-24851
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:N/VA:N/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-02-05
Source: https://github.com/advisories/GHSA-jq9f-gm9w-rwm9
Type: github-advisory

## Affected
- Go: `github.com/openfga/openfga` — affected >=1.8.5 <1.11.3

## Details
### Impact
OpenFGA v1.8.5 to v1.11.2 ( openfga-0.2.22 <= Helm chart <= openfga-0.2.51, v.1.8.5 <= docker <= v.1.11.2) are vulnerable to improper policy enforcement when certain Check calls are executed.


### Affected Users
Users are affected by this vulnerability if all of the following preconditions are met:
- OpenFGA v1.8.5 to v1.11.2 is being used
- The model has a relation directly assignable by a [type bound public access](https://openfga.dev/docs/concepts#what-is-type-bound-public-access) and assignable by type bound non-public access
- A tuple is assigned for the relation that is a type bound public access
- A tuple is assigned for the same object with the same relation that is not type bound public access
- A tuple is assigned for a different object that has an object ID lexicographically larger with the same user and relation which is not type bound public access


### Fix
Upgrade to v1.11.3. This upgrade is backwards compatible.

### Workaround
None

## References
- https://github.com/openfga/openfga/security/advisories/GHSA-jq9f-gm9w-rwm9
- https://nvd.nist.gov/vuln/detail/CVE-2026-24851
- https://github.com/openfga/openfga/commit/1bb5eddf4a3d2fc718aab7914b8f9a1200d2f7ee
- https://github.com/openfga/openfga
- https://github.com/openfga/openfga/releases/tag/v1.11.3
