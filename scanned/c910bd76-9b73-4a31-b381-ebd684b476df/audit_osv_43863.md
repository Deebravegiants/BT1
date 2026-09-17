# [H] CVE-2026-75465

## Summary
Severity: High
Advisory: CVE-2026-75465
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-75465
Type: osv

## Details
The /api.php/user/get_list endpoint in Maccms v10 v2026.1000.4055 is vulnerable to an Incorrect Access Control issue. The interface fails to perform any authentication or authorization checks. An unauthenticated remote attacker can send a crafted HTTP GET request with limit and offset parameters to paginate and retrieve sensitive information of all registered users.

## References
- https://github.com/magicblack/maccms10/releases/tag/v2026.1000.4055
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75465.json
- https://github.com/returnwrong/returnwrong-security-advisories/blob/main/CVE-2026-75465.md
- https://nvd.nist.gov/vuln/detail/CVE-2026-75465
