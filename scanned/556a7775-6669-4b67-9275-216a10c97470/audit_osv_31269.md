# [M] Exposure of Token in open-webui/open-webui

## Summary
Severity: Medium
Advisory: CVE-2024-7049
CVSS: 5.4 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2024-10-10
Source: https://osv.dev/vulnerability/CVE-2024-7049
Type: osv

## Details
In version v0.3.8 of open-webui/open-webui, a vulnerability exists where a token is returned when a user with a pending role logs in. This allows the user to perform actions without admin confirmation, bypassing the intended approval process.

## References
- https://huntr.com/bounties/ee9e3532-8ef1-4599-bb59-b8e2ba43a1fc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/7xxx/CVE-2024-7049.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-7049
