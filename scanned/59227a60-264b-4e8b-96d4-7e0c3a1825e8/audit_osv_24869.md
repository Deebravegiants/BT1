# [M] Apps Framework allows install requests from regular members via an internal path

## Summary
Severity: Medium
Advisory: CVE-2023-2784
CVSS: 4.2 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:N/A:L)
Published: 2023-06-16
Source: https://osv.dev/vulnerability/CVE-2023-2784
Type: osv

## Details
Mattermost fails to verify if the requestor is a sysadmin or not, before allowing `install` requests to the Apps allowing a regular user send install requests to the Apps.

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/2xxx/CVE-2023-2784.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-2784
