# [C] Casdoor arbitrary file write vulnerability

## Summary
Severity: Critical
Advisory: GHSA-9vm3-r8gq-cr6x
CVE: CVE-2022-38638
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2022-09-10
Source: https://github.com/advisories/GHSA-9vm3-r8gq-cr6x
Type: github-advisory

## Affected
- Go: `github.com/casdoor/casdoor` — affected >=0 <1.103.1

## Details
Casdoor v1.97.3 was discovered to contain an arbitrary file write vulnerability via the fullFilePath parameter at /api/upload-resource.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-38638
- https://github.com/casdoor/casdoor/issues/1035
- https://github.com/casdoor/casdoor/issues/1063
- https://github.com/casdoor/casdoor/commit/411d76798d73446fff4a0244f0475f1ea8bf42dc
- https://github.com/casdoor/casdoor
- https://github.com/casdoor/casdoor/releases/tag/v1.103.1
