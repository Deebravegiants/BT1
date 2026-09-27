# [M] Denial of Service via Board Import Zip Bomb

## Summary
Severity: Medium
Advisory: CVE-2023-48268
Aliases: GHSA-j4c3-3h73-74m9
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2023-11-27
Source: https://osv.dev/vulnerability/CVE-2023-48268
Type: osv

## Details
Mattermost fails to limit the amount of data extracted from compressed archives during board import in Mattermost Boards allowing an attacker to consume excessive resources, possibly leading to Denial of Service, by importing a board using a specially crafted zip (zip bomb).

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/48xxx/CVE-2023-48268.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-48268
