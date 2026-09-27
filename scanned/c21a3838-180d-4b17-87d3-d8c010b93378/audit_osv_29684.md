# [H] eLabFTW contains a direct and indirect information disclosure

## Summary
Severity: High
Advisory: CVE-2024-45408
Aliases: GHSA-2c83-6j74-w8r5
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-10-01
Source: https://osv.dev/vulnerability/CVE-2024-45408
Type: osv

## Details
eLabFTW is an open source electronic lab notebook for research labs. An incorrect permission check has been found that could allow an authenticated user to access several kinds of otherwise restricted information. If anonymous access is allowed (something disabled by default), this extends to anyone. Users are advised to upgrade to at least version 5.1.0.  System administrators can disable anonymous access in the System configuration panel.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45408.json
- https://github.com/elabftw/elabftw/security/advisories/GHSA-2c83-6j74-w8r5
- https://nvd.nist.gov/vuln/detail/CVE-2024-45408
