# [M] Log Flooding due to specially crafted requests in different endpoints

## Summary
Severity: Medium
Advisory: CVE-2023-48369
Aliases: GHSA-3487-3j7c-7gwj
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2023-11-27
Source: https://osv.dev/vulnerability/CVE-2023-48369
Type: osv

## Details
Mattermost fails to limit the log size of server logs allowing an attacker sending specially crafted requests to different endpoints to potentially overflow the log.

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/48xxx/CVE-2023-48369.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-48369
