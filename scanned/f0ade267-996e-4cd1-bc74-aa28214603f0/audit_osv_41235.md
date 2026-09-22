# [C] AutoBangumi < 3.2.8 - Hard-coded Default Credentials via add_default_user()

## Summary
Severity: Critical
Advisory: CVE-2026-58466
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-02
Source: https://osv.dev/vulnerability/CVE-2026-58466
Type: osv

## Details
AutoBangumi before 3.2.8 contains a hard-coded default credentials vulnerability that allows unauthenticated attackers to authenticate as the administrator by using the publicly known default credentials seeded at startup via add_default_user() in the database user module when the users table is empty. Attackers can submit the default credentials to the authentication login endpoint to gain full control of the application, including RSS feed configuration, downloader configuration, and all authenticated API endpoints.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58466.json
- https://github.com/EstrellaXD/Auto_Bangumi/releases/tag/3.2.8
- https://nvd.nist.gov/vuln/detail/CVE-2026-58466
- https://www.vulncheck.com/advisories/autobangumi-hard-coded-default-credentials-via-add-default-user
- https://github.com/EstrellaXD/Auto_Bangumi/issues/1041
- https://github.com/EstrellaXD/Auto_Bangumi/commit/487bdfec545e805ae416e6ddf28651bd274d6a73
- https://github.com/EstrellaXD/Auto_Bangumi
