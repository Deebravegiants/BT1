# [M] CNCF K3s Kubernetes kubelet configuration exposes credentials

## Summary
Severity: Medium
Advisory: GHSA-864f-7xjm-2jp2
CVE: CVE-2025-46599
CWE: CWE-1188
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2025-04-25
Source: https://github.com/advisories/GHSA-864f-7xjm-2jp2
Type: github-advisory

## Affected
- Go: `github.com/k3s-io/k3s` — affected >=1.32.0-rc1 <1.32.4-rc1

## Details
CNCF K3s 1.32 before 1.32.4-rc1+k3s1 has a Kubernetes kubelet configuration change with the unintended consequence that, in some situations, ReadOnlyPort is set to 10255. For example, the default behavior of a K3s online installation might allow unauthenticated access to this port, exposing credentials.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-46599
- https://github.com/f1veT/BUG/issues/2
- https://github.com/k3s-io/k3s/issues/12164
- https://github.com/k3s-io/k3s/commit/097b63e588e3c844cdf9b967bcd0a69f4fc0aa0a
- https://cloud.google.com/kubernetes-engine/docs/how-to/disable-kubelet-readonly-port
- https://github.com/k3s-io/k3s
- https://github.com/k3s-io/k3s/compare/v1.32.3+k3s1...v1.32.4-rc1+k3s1
- https://pkg.go.dev/vuln/GO-2025-3646
