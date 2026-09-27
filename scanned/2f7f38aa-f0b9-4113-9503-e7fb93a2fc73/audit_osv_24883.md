# [M] Stack exhaustion in PreparePostForClientWithEmbedsAndImages

## Summary
Severity: Medium
Advisory: CVE-2023-2793
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-06-16
Source: https://osv.dev/vulnerability/CVE-2023-2793
Type: osv

## Details
Mattermost fails to validate links on external websites when constructing a preview for a linked website, allowing an attacker to cause a denial-of-service by a linking to a specially crafted webpage in a message.

## References
- https://mattermost.com/security-updates/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/2xxx/CVE-2023-2793.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-2793
