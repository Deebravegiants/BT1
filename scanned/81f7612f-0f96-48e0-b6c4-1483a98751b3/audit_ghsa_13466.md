# [C] KubePi Privilege Escalation vulnerability

## Summary
Severity: Critical
Advisory: GHSA-757p-vx43-fp9r
CVE: CVE-2023-37917
CWE: CWE-269
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:L (CVSS_V3)
Published: 2023-07-21
Source: https://github.com/advisories/GHSA-757p-vx43-fp9r
Type: github-advisory

## Affected
- Go: `github.com/KubeOperator/kubepi` — affected >=0 <1.6.5

## Details
### Summary
A normal user has permission to create/update users, they can become admin by editing the `isadmin` value in the request


### PoC
Change the value of the `isadmin` field in the request to true:
https://drive.google.com/file/d/1e8XJbIFIDXaFiL-dqn0a0b6u7o3CwqSG/preview

### Impact
Elevate user privileges

## References
- https://github.com/1Panel-dev/KubePi/security/advisories/GHSA-757p-vx43-fp9r
- https://nvd.nist.gov/vuln/detail/CVE-2023-37917
- https://drive.google.com/file/d/1e8XJbIFIDXaFiL-dqn0a0b6u7o3CwqSG/preview
- https://github.com/1Panel-dev/KubePi
- https://github.com/1Panel-dev/KubePi/releases/tag/v1.6.5
