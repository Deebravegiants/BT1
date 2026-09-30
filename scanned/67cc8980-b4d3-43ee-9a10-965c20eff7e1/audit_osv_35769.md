# [M] Denial of service via resource exhaustion in Mattermost

## Summary
Severity: Medium
Advisory: CVE-2026-14298
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-14298
Type: osv

## Details
Mattermost versions 11.9.x <= 11.9.0, 11.8.x <= 11.8.4, 11.7.x <= 11.7.7, 10.11.x <= 10.11.22 fail to properly limit resource consumption when processing certain user-supplied input, which allows an authenticated user to cause a denial of service. Mattermost Advisory ID: MMSA-2026-00713

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/14xxx/CVE-2026-14298.json
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2026-14298
