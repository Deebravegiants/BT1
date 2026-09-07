# [M] Improperly Implemented path matching for in-toto-golang

## Summary
Severity: Medium
Advisory: GHSA-vrxp-mg9f-hwf3
CVE: CVE-2021-41087
CWE: CWE-22, CWE-345
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2021-09-22
Source: https://github.com/advisories/GHSA-vrxp-mg9f-hwf3
Type: github-advisory

## Affected
- Go: `github.com/in-toto/in-toto-golang` — affected >=0 <0.3.0

## Details
### Impact
Authenticated attackers posing as functionaries (i.e., within a trusted set of users for a layout) are able to create attestations that may bypass DISALLOW rules in the same layout. An attacker with access to trusted private keys, may issue an attestation that contains a disallowed artifact by including path traversal semantics (e.g., foo vs dir/../foo).

### Patches
The problem has been fixed in version 0.3.0.

### Workarounds
Exploiting this vulnerability is dependent on the specific policy applied.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [in-toto-golang](http://github.com/in-toto/in-toto-golang)
* Email us at [in-toto-public](mailto:in-toto-public@googlegroups.com)
* If this is a sensitive security-relevant disclosure, please send a PGP encrypted email to santiagotorres@purdue.edu or jcappos@nyu.edu

## References
- https://github.com/in-toto/in-toto-golang/security/advisories/GHSA-vrxp-mg9f-hwf3
- https://nvd.nist.gov/vuln/detail/CVE-2021-41087
- https://github.com/in-toto/in-toto-golang/commit/f2c57d1e0f15e3ffbeac531829c696b72ecc4290
- https://github.com/in-toto/in-toto-golang
