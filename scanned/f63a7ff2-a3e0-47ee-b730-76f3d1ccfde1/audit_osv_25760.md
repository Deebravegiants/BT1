# [M] Permalink previews displayed for posts in archived channels even if users are disallowed to view archived channels

## Summary
Severity: Medium
Advisory: CVE-2023-43754
Aliases: GHSA-jjr7-372r-cx7x
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-11-27
Source: https://osv.dev/vulnerability/CVE-2023-43754
Type: osv

## Details
Mattermost fails to check whether the  “Allow users to view archived channels”  setting is enabled during permalink previews display, allowing members to view permalink previews of archived channels even if the “Allow users to view archived channels” setting is disabled.

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/43xxx/CVE-2023-43754.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-43754
