# [H] Widoco Path Traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-jj8r-jw42-mw4w
CVE: CVE-2022-4772
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-28
Source: https://github.com/advisories/GHSA-jj8r-jw42-mw4w
Type: github-advisory

## Affected
- Maven: `com.github.dgarijo:Widoco` — affected >=0

## Details
A vulnerability was found in Widoco and classified as critical. Affected by this issue is the function `unZipIt` of the file `src/main/java/widoco/WidocoUtils.java`. The manipulation leads to path traversal. It is possible to launch the attack on the local host. The name of the patch is f2279b76827f32190adfa9bd5229b7d5a147fa92. It is recommended to apply a patch to fix this issue. VDB-216914 is the identifier assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4772
- https://github.com/dgarijo/Widoco/pull/551
- https://github.com/dgarijo/Widoco/commit/f2279b76827f32190adfa9bd5229b7d5a147fa92
- https://github.com/dgarijo/Widoco
- https://vuldb.com/?ctiid.216914
- https://vuldb.com/?id.216914
