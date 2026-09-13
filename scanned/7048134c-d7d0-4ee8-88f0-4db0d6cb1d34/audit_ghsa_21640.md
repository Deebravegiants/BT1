# [M] Kubernetes Arbitrary Command Injection

## Summary
Severity: Medium
Advisory: GHSA-wqwf-x5cj-rg56
CVE: CVE-2018-1002101
CWE: CWE-78
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-wqwf-x5cj-rg56
Type: github-advisory

## Affected
- Go: `k8s.io/kubernetes` — affected >=1.9.0 <1.9.10
- Go: `k8s.io/kubernetes` — affected >=1.10.0 <1.10.6
- Go: `k8s.io/kubernetes` — affected >=1.11.0 <1.11.2

## Details
In Kubernetes versions 1.9.0-1.9.9, 1.10.0-1.10.5, and 1.11.0-1.11.1, user input was handled insecurely while setting up volume mounts on Windows nodes, which could lead to command line argument injection.

### Specific Go Packages Affected
k8s.io/kubernetes/pkg/util/mount

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1002101
- https://github.com/kubernetes/kubernetes/issues/65750
- https://github.com/kubernetes/kubernetes/pull/65751
- https://github.com/kubernetes/kubernetes/commit/d65039c56ce4de5f2efdc38aa1284eeb95f89169
- https://security.netapp.com/advisory/ntap-20190416-0008
- http://www.securityfocus.com/bid/106238
