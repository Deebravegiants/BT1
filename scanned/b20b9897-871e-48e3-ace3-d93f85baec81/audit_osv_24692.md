# [M] DB username/password revealed in application logs

## Summary
Severity: Medium
Advisory: CVE-2023-2514
CVSS: 6.7 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:L)
Published: 2023-05-12
Source: https://osv.dev/vulnerability/CVE-2023-2514
Type: osv

## Details
Mattermost Sever fails to redact the DB username and password before emitting an application log during server initialization.

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/2xxx/CVE-2023-2514.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-2514
