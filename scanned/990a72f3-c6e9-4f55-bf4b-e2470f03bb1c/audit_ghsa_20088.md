# [M] OpenShift OSIN vulnerable to Observable Timing Discrepancy

## Summary
Severity: Medium
Advisory: GHSA-m7qp-cj9p-gj85
CVE: CVE-2021-4294
CWE: CWE-203, CWE-208
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-12-28
Source: https://github.com/advisories/GHSA-m7qp-cj9p-gj85
Type: github-advisory

## Affected
- Go: `github.com/openshift/osin` — affected >=0 <1.0.2-0.20210113124101-8612686d6dda

## Details
A vulnerability was found in OpenShift OSIN. It has been classified as problematic. This affects the function `ClientSecretMatches/CheckClientSecret`. The manipulation of the argument secret leads to observable timing discrepancy. The name of the patch is 8612686d6dda34ae9ef6b5a974e4b7accb4fea29. It is recommended to apply a patch to fix this issue. The associated identifier of this vulnerability is VDB-216987.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-4294
- https://github.com/openshift/osin/pull/200
- https://github.com/openshift/osin/commit/8612686d6dda34ae9ef6b5a974e4b7accb4fea29
- https://github.com/openshift/osin
- https://pkg.go.dev/vuln/GO-2022-1201
- https://vuldb.com/?ctiid.216987
- https://vuldb.com/?id.216987
