# [M] Denial of Service via specially crafted gif image

## Summary
Severity: Medium
Advisory: CVE-2023-3614
Aliases: BIT-mattermost-2023-3614
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L)
Published: 2023-07-17
Source: https://osv.dev/vulnerability/CVE-2023-3614
Type: osv

## Details
Mattermost fails to properly validate a gif image file, allowing an attacker to consume a significant amount of server resources, making the server unresponsive for an extended period of time by linking to specially crafted image file.

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3614.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3614
