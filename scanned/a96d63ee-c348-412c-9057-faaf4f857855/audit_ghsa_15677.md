# [H] Kubernetes sets incorrect permissions on Windows containers logs

## Summary
Severity: High
Advisory: GHSA-82m2-cv7p-4m75
CVE: CVE-2024-5321
CWE: CWE-276
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2024-07-18
Source: https://github.com/advisories/GHSA-82m2-cv7p-4m75
Type: github-advisory

## Affected
- Go: `k8s.io/kubernetes` — affected >=0 <1.27.16
- Go: `k8s.io/kubernetes` — affected >=1.28.0 <1.28.12
- Go: `k8s.io/kubernetes` — affected >=1.29.0 <1.29.7
- Go: `k8s.io/kubernetes` — affected >=1.30.0 <1.30.3

## Details
A security issue was discovered in Kubernetes clusters with Windows nodes where BUILTIN\Users may be able to read container logs and NT AUTHORITY\Authenticated Users may be able to modify container logs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-5321
- https://github.com/kubernetes/kubernetes/issues/126161
- https://github.com/kubernetes/kubernetes/commit/23660a78ae462a6c8c75ac7ffd9af97550dda1aa
- https://github.com/kubernetes/kubernetes/commit/84beb2915fa28ae477fe0676be8ba94ccd2b811a
- https://github.com/kubernetes/kubernetes/commit/90589b8f63d28bcd3db89749950ebc48ed07c190
- https://github.com/kubernetes/kubernetes/commit/de2033033b1d202ecaaa79d41861a075df8b49c1
- https://github.com/kubernetes/kubernetes
- https://groups.google.com/g/kubernetes-security-announce/c/81c0BHkKNt0
