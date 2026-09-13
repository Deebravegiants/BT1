# [H] ReDOS in Vfsjfilechooser2

## Summary
Severity: High
Advisory: GHSA-c7fh-chf7-jr5x
CVE: CVE-2021-29061
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-c7fh-chf7-jr5x
Type: github-advisory

## Affected
- Maven: `com.github.fracpete:vfsjfilechooser2` — affected >=0 <0.2.9

## Details
A Regular Expression Denial of Service (ReDOS) vulnerability was discovered in Vfsjfilechooser2 which occurs when the application attempts to validate crafted URIs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-29061
- https://github.com/fracpete/vfsjfilechooser2/issues/7
- https://github.com/fracpete/vfsjfilechooser2/commit/9c9f2c317f3de5ece60a3ae28c371e9796e3909b
- https://github.com/fracpete/vfsjfilechooser2/releases/tag/vfsjfilechooser2-0.2.9
- https://github.com/yetingli/PoCs/blob/main/CVE-2021-29061/Vfsjfilechooser2.md
- https://github.com/yetingli/SaveResults/blob/main/md/vfsjfilechooser2.md
