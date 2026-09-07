# [H] KubeOperator allows unauthorized access to system API

## Summary
Severity: High
Advisory: GHSA-jxgp-jgh3-8jc8
CVE: CVE-2023-22480
CWE: CWE-285, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-01-09
Source: https://github.com/advisories/GHSA-jxgp-jgh3-8jc8
Type: github-advisory

## Affected
- Go: `github.com/KubeOperator/KubeOperator` — affected >=0

## Details
### Summary

Unauthorized access refers to the ability to bypass the system's preset permission settings to access some API interfaces. The attack exploits a flaw in how online applications handle routing permissions.

### Affected Version

<= v3.16.3

### Patches

The vulnerability has been fixed in v3.16.3.

https://github.com/KubeOperator/KubeOperator/commit/7ef42bf1c16900d13e6376f8be5ecdbfdfb44aaf

### Workarounds

It is recommended to upgrade the version to v3.16.4.

### For more information

If you have any questions or comments about this advisory, please open an issue.

### References

https://github.com/KubeOperator/KubeOperator/releases/tag/v3.16.4

## References
- https://github.com/KubeOperator/KubeOperator/security/advisories/GHSA-jxgp-jgh3-8jc8
- https://nvd.nist.gov/vuln/detail/CVE-2023-22480
- https://github.com/KubeOperator/KubeOperator/commit/7ef42bf1c16900d13e6376f8be5ecdbfdfb44aaf
- https://github.com/KubeOperator/KubeOperator
- https://github.com/KubeOperator/KubeOperator/releases/tag/v3.16.4
