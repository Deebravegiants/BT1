# [H] GoPistolet vulnerable to Improper Resource Shutdown or Release

## Summary
Severity: High
Advisory: GHSA-wr8h-w969-36m8
CVE: CVE-2015-10085
CWE: CWE-404
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-02-21
Source: https://github.com/advisories/GHSA-wr8h-w969-36m8
Type: github-advisory

## Affected
- Go: `github.com/gopistolet/gopistolet` — affected >=0 <0.0.0-20210418093520-a5395f728f8d

## Details
A vulnerability was found in GoPistolet. It has been declared as problematic. This vulnerability affects unknown code of the component MTA. The manipulation leads to denial of service. Continious delivery with rolling releases is used by this product. Therefore, no version details of affected nor updated releases are available. The name of the patch is b91aa4674d460993765884e8463c70e6d886bc90. It is recommended to apply a patch to fix this issue. VDB-221506 is the identifier assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-10085
- https://github.com/gopistolet/gopistolet/pull/27
- https://github.com/gopistolet/gopistolet/commit/b91aa4674d460993765884e8463c70e6d886bc90
- https://github.com/gopistolet/gopistolet
- https://vuldb.com/?ctiid.221506
- https://vuldb.com/?id.221506
