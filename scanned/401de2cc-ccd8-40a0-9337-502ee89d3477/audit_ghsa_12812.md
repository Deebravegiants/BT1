# [M] easy-scrypt Observable Timing Discrepancy vulnerability

## Summary
Severity: Medium
Advisory: GHSA-r894-5r7v-7rx3
CVE: CVE-2014-125055
CWE: CWE-208
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-01-07
Source: https://github.com/advisories/GHSA-r894-5r7v-7rx3
Type: github-advisory

## Affected
- Go: `github.com/agnivade/easy-scrypt` — affected >=0 <1.0.0

## Details
A vulnerability, which was classified as problematic, was found in agnivade easy-scrypt. Affected is the function `VerifyPassphrase` of the file `scrypt.go`. The manipulation leads to observable timing discrepancy. Upgrading to version 1.0.0 can address this issue. The name of the patch is 477c10cf3b144ddf96526aa09f5fdea613f21812. It is recommended to upgrade the affected component. The identifier of this vulnerability is VDB-217596.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-125055
- https://github.com/agnivade/easy-scrypt/commit/477c10cf3b144ddf96526aa09f5fdea613f21812
- https://github.com/agnivade/easy-scrypt
- https://github.com/agnivade/easy-scrypt/releases/tag/v1.0.0
- https://vuldb.com/?ctiid.217596
- https://vuldb.com/?id.217596
