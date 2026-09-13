# [H] Access Restriction Bypass in kubernetes

## Summary
Severity: High
Advisory: GHSA-xx8c-m748-xr4j
CVE: CVE-2016-1905
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-xx8c-m748-xr4j
Type: github-advisory

## Affected
- Go: `github.com/kubernetes/kubernetes` — affected >=0 <1.2.0-alpha.6

## Details
The API server in Kubernetes does not properly check admission control, which allows remote authenticated users to access additional resources via a crafted patched object.

### Specific Go Packages Affected
github.com/kubernetes/kubernetes/pkg/apiserver

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-1905
- https://github.com/kubernetes/kubernetes/issues/19479
- https://github.com/kubernetes/kubernetes/commit/9e6912384a5bc714f2a780b870944a8cee264a22
- https://access.redhat.com/errata/RHSA-2016:0070
- https://access.redhat.com/errata/RHSA-2016:0351
- https://access.redhat.com/security/cve/CVE-2016-1905
- https://bugzilla.redhat.com/show_bug.cgi?id=1297910
