# [M] Fluid vulnerable to OS Command Injection for Fluid Users with JuicefsRuntime

## Summary
Severity: Medium
Advisory: GHSA-wx8q-4gm9-rj2g
CVE: CVE-2023-51699
CWE: CWE-78
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:H/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-03-15
Source: https://github.com/advisories/GHSA-wx8q-4gm9-rj2g
Type: github-advisory

## Affected
- Go: `github.com/fluid-cloudnative/fluid` — affected >=0 <0.9.3

## Details
### Impact
OS command injection vulnerability within the Fluid project's JuicefsRuntime can potentially allow an authenticated user, who has the authority to create or update the K8s CRD Dataset/JuicefsRuntime, to execute arbitrary OS commands within the juicefs related containers. This could lead to unauthorized access, modification or deletion of data.

### Patches
For users who're using version < 0.9.3 with JuicefsRuntime， upgrade to v0.9.3.

### References
_Are there any links users can visit to find out more?_

### Credits

Special thanks to the discovers of this issue:

Xiaozheng Zhang [xiaozheng_zhang@outlook.com](xiaozheng_zhang@outlook.com)

## References
- https://github.com/fluid-cloudnative/fluid/security/advisories/GHSA-wx8q-4gm9-rj2g
- https://nvd.nist.gov/vuln/detail/CVE-2023-51699
- https://github.com/fluid-cloudnative/fluid/commit/02b7cd8b79a26092df95d625664994bda485c722
- https://github.com/fluid-cloudnative/fluid/commit/e0184cff8790ad000c3e8943392c7f544fad7d66
- https://github.com/fluid-cloudnative/fluid
