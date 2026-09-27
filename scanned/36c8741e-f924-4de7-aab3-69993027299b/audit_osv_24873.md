# [M] Collapsed Reply Threads APIs leak message contents from private channels

## Summary
Severity: Medium
Advisory: CVE-2023-2787
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-06-16
Source: https://osv.dev/vulnerability/CVE-2023-2787
Type: osv

## Details
Mattermost fails to check channel membership when accessing message threads, allowing an attacker to access arbitrary posts by using the message threads API.

## References
- https://mattermost.com/security-updates/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/2xxx/CVE-2023-2787.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-2787
