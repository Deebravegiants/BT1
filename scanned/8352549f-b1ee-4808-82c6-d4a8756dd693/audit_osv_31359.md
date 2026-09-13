# [H] Missing Authentication Check in parisneo/lollms-webui

## Summary
Severity: High
Advisory: CVE-2024-9919
CVSS: 8.4 (CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-9919
Type: osv

## Details
A missing authentication check in the uninstall endpoint of parisneo/lollms-webui V13 allows attackers to perform unauthorized directory deletions. The /uninstall/{app_name} API endpoint does not call the check_access() function to verify the client_id, enabling attackers to delete directories without proper authentication.

## References
- https://huntr.com/bounties/5c00f56b-32a8-4e26-a4e3-de64f139da6b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/9xxx/CVE-2024-9919.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-9919
