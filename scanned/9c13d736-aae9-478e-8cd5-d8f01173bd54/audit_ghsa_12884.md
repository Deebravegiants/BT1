# [H] KubePi session fixation attack allows an attacker to hijack a legitimate user session.

## Summary
Severity: High
Advisory: GHSA-v4w5-r2xc-7f8h
CVE: CVE-2023-22479
CWE: CWE-384
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-09
Source: https://github.com/advisories/GHSA-v4w5-r2xc-7f8h
Type: github-advisory

## Affected
- Go: `github.com/KubeOperator/kubepi` — affected >=0 <1.6.4

## Details
### Summary
A session fixation attack allows an attacker to hijack a legitimate user session. The attack investigates a flaw in how the online application handles the session ID, especially the susceptible web application.

### Affected Version
<= v1.6.3

### Patches
The vulnerability has been fixed in [v1.6.4](https://github.com/KubeOperator/KubePi/releases/tag/v1.6.4).

https://github.com/KubeOperator/KubePi/commit/1e9c550356c1a425a742480efcf743d373e98dcb : A session fixation attack allows an attacker to hijack a legitimate user session.

### Workarounds
It is recommended to upgrade the version to [v1.6.4](https://github.com/KubeOperator/KubePi/releases/tag/v1.6.4).

### For more information
If you have any questions or comments about this advisory, please [open an issue](https://github.com/KubeOperator/KubePi/issues).

This vulnerability is reported by [sachinh09](https://huntr.dev/users/sachinh09/) from [huntr.dev](https://huntr.dev/).

## References
- https://github.com/1Panel-dev/KubePi/security/advisories/GHSA-v4w5-r2xc-7f8h
- https://github.com/KubeOperator/KubePi/security/advisories/GHSA-v4w5-r2xc-7f8h
- https://nvd.nist.gov/vuln/detail/CVE-2023-22479
- https://github.com/KubeOperator/KubePi/commit/1e9c550356c1a425a742480efcf743d373e98dcb
- https://github.com/KubeOperator/KubePi
- https://github.com/KubeOperator/KubePi/releases/tag/v1.6.4
