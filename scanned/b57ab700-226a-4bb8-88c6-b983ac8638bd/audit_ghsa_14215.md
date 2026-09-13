# [M] CubeFS allows Kubernetes cluster-level privilege escalation

## Summary
Severity: Medium
Advisory: GHSA-9337-8c6c-c2xg
CVE: CVE-2023-30512
CWE: CWE-732
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-04-12
Source: https://github.com/advisories/GHSA-9337-8c6c-c2xg
Type: github-advisory

## Affected
- Go: `github.com/cubefs/cubefs` — affected >=0

## Details
CubeFS through 3.2.1 allows Kubernetes cluster-level privilege escalation. This occurs because DaemonSet has cfs-csi-cluster-role and can thus list all secrets, including the admin secret.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-30512
- https://github.com/cubefs/cubefs/issues/1882
- https://github.com/cubefs/cubefs
