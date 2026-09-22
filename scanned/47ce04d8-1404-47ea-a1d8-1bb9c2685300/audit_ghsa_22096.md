# [M] Kubernetes arbitrary file overwrite

## Summary
Severity: Medium
Advisory: GHSA-mm7g-f2gg-cw8g
CVE: CVE-2017-1002102
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-mm7g-f2gg-cw8g
Type: github-advisory

## Affected
- Go: `k8s.io/kubernetes` — affected >=1.3.0 <1.7.14
- Go: `k8s.io/kubernetes` — affected >=1.8.0 <1.8.9
- Go: `k8s.io/kubernetes` — affected >=1.9.0 <1.9.4

## Details
In Kubernetes versions 1.3.x, 1.4.x, 1.5.x, 1.6.x and prior to versions 1.7.14, 1.8.9 and 1.9.4 containers using a secret, configMap, projected or downwardAPI volume can trigger deletion of arbitrary files/directories from the nodes where they are running.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1002102
- https://github.com/kubernetes/kubernetes/issues/60814
- https://access.redhat.com/errata/RHSA-2018:0475
- https://github.com/kubernetes/kubernetes
