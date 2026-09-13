# [C] Panindex uses hard coded cyptographic key

## Summary
Severity: Critical
Advisory: CVE-2023-27583
Aliases: GHSA-82wq-gmw8-g87v
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-13
Source: https://osv.dev/vulnerability/CVE-2023-27583
Type: osv

## Details
PanIndex is a network disk directory index. In Panindex prior to version 3.1.3,  a hard-coded JWT key `PanIndex` is used. An attacker can use the hard-coded JWT key to sign JWT token and perform any actions as a user with admin privileges. Version 3.1.3 has a patch for the issue. As a workaround, one may change the JWT key in the source code before compiling the project.

## References
- https://github.com/px-org/PanIndex/releases/tag/v3.1.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/27xxx/CVE-2023-27583.json
- https://github.com/px-org/PanIndex/security/advisories/GHSA-82wq-gmw8-g87v
- https://nvd.nist.gov/vuln/detail/CVE-2023-27583
- https://github.com/px-org/PanIndex/commit/f7ec0c5739af055ad3a825a20294a5c01ada3302
