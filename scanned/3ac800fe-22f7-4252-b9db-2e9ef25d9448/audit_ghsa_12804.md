# [H] KubePi may allow unauthorized access to system API

## Summary
Severity: High
Advisory: GHSA-gqx8-hxmv-c4v4
CVE: CVE-2023-22478
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-01-09
Source: https://github.com/advisories/GHSA-gqx8-hxmv-c4v4
Type: github-advisory

## Affected
- Go: `github.com/KubeOperator/kubepi` — affected >=0 <1.6.4

## Details
### Summary
Unauthorized access refers to the ability to bypass the system's preset permission settings to access some API interfaces. The attack exploits a flaw in how online applications handle routing permissions.

### Affected Version
<= v1.6.3

### Patches
The vulnerability has been fixed in v1.6.4.

https://github.com/KubeOperator/KubePi/commit/0c6774bf5d9003ae4d60257a3f207c131ff4a6d6

### Workarounds
It is recommended to upgrade the version to v1.6.4.

### For more information
If you have any questions or comments about this advisory, please open an issue.

### References
https://github.com/KubeOperator/KubePi/releases/tag/v1.6.4

## References
- https://github.com/1Panel-dev/KubePi/security/advisories/GHSA-gqx8-hxmv-c4v4
- https://github.com/KubeOperator/KubePi/security/advisories/GHSA-gqx8-hxmv-c4v4
- https://nvd.nist.gov/vuln/detail/CVE-2023-22478
- https://github.com/KubeOperator/KubePi/commit/0c6774bf5d9003ae4d60257a3f207c131ff4a6d6
- https://github.com/KubeOperator/KubePi
- https://github.com/KubeOperator/KubePi/releases/tag/v1.6.4
