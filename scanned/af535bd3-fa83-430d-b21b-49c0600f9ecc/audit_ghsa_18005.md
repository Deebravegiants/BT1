# [M] OpenFGA Authorization Bypass 

## Summary
Severity: Medium
Advisory: GHSA-mgh9-4mwp-fg55
CVE: CVE-2025-55213
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:N/VA:N/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2025-08-18
Source: https://github.com/advisories/GHSA-mgh9-4mwp-fg55
Type: github-advisory

## Affected
- Go: `github.com/openfga/openfga` — affected >=1.9.3 <1.9.5

## Details
### Overview
OpenFGA v1.9.3 to v1.9.4 ( openfga-0.2.40 <= Helm chart <= openfga-0.2.41, v1.9.3 <= docker <= v.1.9.4) are vulnerable to improper policy enforcement when certain Check and ListObject calls are executed.

### Am I Affected?
You are affected by this vulnerability if you are using OpenFGA v1.9.3 to v1.9.4, specifically under the following preconditions:
- Calling Check API or ListObjects with an [authorization model](https://openfga.dev/docs/concepts#what-is-an-authorization-model) that has a relationship directly assignable by more than 1 [userset](https://openfga.dev/docs/modeling/building-blocks/usersets) with same [type](https://openfga.dev/docs/concepts#what-is-a-type), and
- There are check or list object queries that rely on the above relationship, and
- You have userset tuples that are assigned to the above relationship


### Fix
Upgrade to v1.9.5. This upgrade is backwards compatible.

### Workaround
Downgrade to v1.9.2 with enable-check-optimizations removed from OPENFGA_EXPERIMENTALS

### Acknowledgments
OpenFGA would like Dominic Harries and rrozza-apolitical to thank for discovering this vulnerability.

## References
- https://github.com/openfga/openfga/security/advisories/GHSA-mgh9-4mwp-fg55
- https://nvd.nist.gov/vuln/detail/CVE-2025-55213
- https://github.com/openfga/openfga/commit/1a7e0e37fc4777c824b2386cac4867a66f3480b0
- https://github.com/openfga/openfga
- https://pkg.go.dev/vuln/GO-2025-3894
