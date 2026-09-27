# [M] KubeSphere IDOR vulnerability

## Summary
Severity: Medium
Advisory: GHSA-p26r-gfgc-c47h
CVE: CVE-2024-46528
CWE: CWE-639
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-10-14
Source: https://github.com/advisories/GHSA-p26r-gfgc-c47h
Type: github-advisory

## Affected
- Go: `github.com/kubesphere/kubesphere` — affected >=4.0.0 <4.1.3
- Go: `github.com/kubesphere/kubesphere` — affected >=3.0.0 <3.4.1

## Details
An Insecure Direct Object Reference (IDOR) vulnerability in KubeSphere v3.4.1 and v4.1.1 allows low-privileged authenticated attackers to access sensitive resources without proper authorization checks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-46528
- https://github.com/kubesphere/kubesphere/issues/6227
- https://github.com/kubesphere/kubesphere
- https://kubesphere.io
- https://okankurtulus.com.tr/2024/09/09/idor-vulnerability-in-kubesphere
- https://pkg.go.dev/vuln/GO-2024-3248
- https://www.kubesphere.io/news/kubesphere-cve-2024-46528
