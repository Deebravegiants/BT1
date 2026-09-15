# [M] Denial of Service via specially crafted block fields in Mattermost Boards

## Summary
Severity: Medium
Advisory: CVE-2023-40703
Aliases: GHSA-c37r-v8jx-7cv2
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2023-11-27
Source: https://osv.dev/vulnerability/CVE-2023-40703
Type: osv

## Details
Mattermost fails to properly limit the characters allowed in different fields of a block in Mattermost Boards allowing a attacker to consume excessive resources, possibly leading to Denial of Service, by patching the field of a block using a specially crafted string.

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/40xxx/CVE-2023-40703.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-40703
