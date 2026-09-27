# [M] KubePi may leak password hash of any user

## Summary
Severity: Medium
Advisory: GHSA-87f6-8gr7-pc6h
CVE: CVE-2023-37916
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-07-21
Source: https://github.com/advisories/GHSA-87f6-8gr7-pc6h
Type: github-advisory

## Affected
- Go: `github.com/KubeOperator/kubepi` — affected >=0 <1.6.5

## Details
### Summary
http://kube.pi/kubepi/api/v1/users/search?pageNum=1&&pageSize=10 leak password of any user (including admin). This leads to password crack attack


### PoC
https://drive.google.com/file/d/1ksdawJ1vShRJyT3wAgpqVmz-Ls6hMA7M/preview

### Impact
- Leaking confidential information.
- Can lead to password cracking attacks

## References
- https://github.com/1Panel-dev/KubePi/security/advisories/GHSA-87f6-8gr7-pc6h
- https://nvd.nist.gov/vuln/detail/CVE-2023-37916
- https://drive.google.com/file/d/1ksdawJ1vShRJyT3wAgpqVmz-Ls6hMA7M/preview
- https://github.com/1Panel-dev/KubePi
- https://github.com/1Panel-dev/KubePi/releases/tag/v1.6.5
