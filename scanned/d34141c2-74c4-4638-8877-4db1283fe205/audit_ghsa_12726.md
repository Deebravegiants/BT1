# [C] dssp vulnerable to Improper Restriction of XML External Entity Reference

## Summary
Severity: Critical
Advisory: GHSA-77cc-w3wm-6whp
CVE: CVE-2016-15011
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-06
Source: https://github.com/advisories/GHSA-77cc-w3wm-6whp
Type: github-advisory

## Affected
- Maven: `be.e_contract.dssp:dssp-client` — affected >=0 <1.3.2

## Details
A vulnerability classified as problematic was found in e-Contract dssp up to 1.3.1. Affected by this vulnerability is the function `checkSignResponse` of the file `dssp-client/src/main/java/be/e_contract/dssp/client/SignResponseVerifier.java`. The manipulation leads to xml external entity reference. Upgrading to version 1.3.2 can address this issue. The name of the patch is ec4238349691ec66dd30b416ec6eaab02d722302. It is recommended to upgrade the affected component. The identifier VDB-217549 was assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-15011
- https://github.com/e-Contract/dssp/commit/ec4238349691ec66dd30b416ec6eaab02d722302
- https://github.com/e-Contract/dssp
- https://github.com/e-Contract/dssp/releases/tag/dssp-1.3.2
- https://vuldb.com/?ctiid.217549
- https://vuldb.com/?id.217549
