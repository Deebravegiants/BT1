# [M] Kubernetes Sensitive Information leak via Log File

## Summary
Severity: Medium
Advisory: GHSA-8mjg-8c8g-6h85
CVE: CVE-2020-8564
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-02-06
Source: https://github.com/advisories/GHSA-8mjg-8c8g-6h85
Type: github-advisory

## Affected
- Go: `github.com/kubernetes/kubernetes` — affected >=1.19.0 <1.19.3
- Go: `github.com/kubernetes/kubernetes` — affected >=1.18.0 <1.18.10
- Go: `github.com/kubernetes/kubernetes` — affected >=0 <1.17.13
- Go: `k8s.io/kubernetes` — affected >=0 <1.20.0-alpha.1

## Details
In Kubernetes clusters using a logging level of at least 4, processing a malformed docker config file will result in the contents of the docker config file being leaked, which can include pull secrets or other registry credentials. This affects < v1.19.3, < v1.18.10, < v1.17.13.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8564
- https://github.com/kubernetes/kubernetes/issues/95622
- https://github.com/kubernetes/kubernetes/pull/94712
- https://github.com/kubernetes/kubernetes/commit/11793434dac97a49bfed0150b56ac63e5dc34634
- https://github.com/kubernetes/kubernetes
- https://groups.google.com/g/kubernetes-security-discuss/c/vm-HcrFUOCs/m/36utxAM5CwAJ
- https://pkg.go.dev/vuln/GO-2021-0066
- https://security.netapp.com/advisory/ntap-20210122-0006
