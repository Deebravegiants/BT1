# [H] Authorization Bypass in Mattermost Legal Hold Plugin Due to Missing Return After Permission Check

## Summary
Severity: High
Advisory: CVE-2026-3524
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-06
Source: https://osv.dev/vulnerability/CVE-2026-3524
Type: osv

## Details
Mattermost Plugin Legal Hold versions <=1.1.4 fail to halt request processing after a failed authorization check in ServeHTTP which allows an authenticated attacker to access, create, download, and delete legal hold data via crafted API requests to the plugin's endpoints. Mattermost Advisory ID: MMSA-2026-00621

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/3xxx/CVE-2026-3524.json
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2026-3524
