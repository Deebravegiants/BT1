# [H] LinkAce affected by SSRF via link creation: NoPrivateIpRule not applied to LinkStoreRequest

## Summary
Severity: High
Advisory: CVE-2026-30953
Aliases: GHSA-f2mp-q78r-7jx7
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-03-10
Source: https://osv.dev/vulnerability/CVE-2026-30953
Type: osv

## Details
LinkAce is a self-hosted archive to collect website links. When a user creates a link via POST /links, the server fetches HTML metadata from the provided URL (LinkRepository::create() calls HtmlMeta::getFromUrl()). The LinkStoreRequest validation rules do not include NoPrivateIpRule, allowing server-side requests to internal network addresses, Docker service hostnames, and cloud metadata endpoints. The project already has a NoPrivateIpRule class (app/Rules/NoPrivateIpRule.php) but it is only applied in FetchController.php (line 99), not in the primary link creation path.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30953.json
- https://github.com/Kovah/LinkAce/security/advisories/GHSA-f2mp-q78r-7jx7
- https://nvd.nist.gov/vuln/detail/CVE-2026-30953
