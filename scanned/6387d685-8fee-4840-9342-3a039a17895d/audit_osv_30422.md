# [M] Nextcloud Server's global credentials of external storages are sent back to the frontend

## Summary
Severity: Medium
Advisory: CVE-2024-52517
Aliases: GHSA-x9q3-c7f8-3rcg
CVSS: 4.6 (CVSS:3.1/AV:P/AC:H/PR:H/UI:R/S:C/C:H/I:N/A:N)
Published: 2024-11-15
Source: https://osv.dev/vulnerability/CVE-2024-52517
Type: osv

## Details
Nextcloud Server is a self hosted personal cloud system. After storing "Global credentials" on the server, the API returns them and adds them into the frontend again, allowing to read them in plain text when an attacker already has access to an active session of a user. It is recommended that the Nextcloud Server is upgraded to 28.0.11, 29.0.8 or 30.0.1 and Nextcloud Enterprise Server is upgraded to 25.0.13.13, 26.0.13.9, 27.1.11.9, 28.0.11, 29.0.8 or 30.0.1.

## References
- https://hackerone.com/reports/2554079
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52517.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-x9q3-c7f8-3rcg
- https://nvd.nist.gov/vuln/detail/CVE-2024-52517
- https://github.com/nextcloud/server/commit/c45ed55f959ff54f3ea23dd2ae1a5868a075c9fe
- https://github.com/nextcloud/server/pull/48359
