# [H] SQL Injection in Cloud Native Computing Foundation Harbor

## Summary
Severity: High
Advisory: GHSA-jr34-mff8-pc6f
CVE: CVE-2019-19029
CWE: CWE-89
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-jr34-mff8-pc6f
Type: github-advisory

## Affected
- Go: `github.com/goharbor/harbor` — affected >=1.7.0 <1.8.6
- Go: `github.com/goharbor/harbor` — affected >=1.9.0 <1.9.3

## Details
Cloud Native Computing Foundation Harbor prior to 1.8.6 and 1.9.3 allows SQL Injection via user-groups in the VMware Harbor Container Registry for the Pivotal Platform.

## References
- https://github.com/goharbor/harbor/security/advisories/GHSA-qcfv-8v29-469w
- https://nvd.nist.gov/vuln/detail/CVE-2019-19029
- https://github.com/goharbor/harbor
- https://github.com/goharbor/harbor/security/advisories
- https://pkg.go.dev/vuln/GO-2022-0853
- https://tanzu.vmware.com/security/cve-2019-19029
