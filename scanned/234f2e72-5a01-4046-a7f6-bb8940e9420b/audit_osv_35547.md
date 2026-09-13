# [M] Denial of service via unbounded document content extraction in Mattermost Server

## Summary
Severity: Medium
Advisory: CVE-2026-10600
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-07-27
Source: https://osv.dev/vulnerability/CVE-2026-10600
Type: osv

## Details
Mattermost versions 11.8.x <= 11.8.0, 11.7.x <= 11.7.3, 11.6.x <= 11.6.5, 10.11.x <= 10.11.20 fail to bound the time and resource consumption of server-side document content extraction which allows an authenticated user with file-upload permission to degrade file uploads for all users on the server via repeatedly uploading small documents that are cheap to upload but expensive to extract, saturating the shared extraction worker pool.. Mattermost Advisory ID: MMSA-2026-00694

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10600.json
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2026-10600
