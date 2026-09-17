# [M] Windows user name disclosure in TGstation

## Summary
Severity: Medium
Advisory: CVE-2023-34243
Aliases: GHSA-w3jx-4x93-76ph
CVSS: 5.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N)
Published: 2023-06-08
Source: https://osv.dev/vulnerability/CVE-2023-34243
Type: osv

## Details
TGstation is a toolset to manage production BYOND servers. In affected versions if a Windows user was registered in tgstation-server (TGS), an attacker could discover their username by brute-forcing the login endpoint with an invalid password. When a valid Windows logon was found, a distinct response would be generated. This issue has been addressed in version 5.12.5. Users are advised to upgrade. Users unable to upgrade may be mitigated by rate-limiting API calls with software that sits in front of TGS in the HTTP pipeline such as fail2ban.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/34xxx/CVE-2023-34243.json
- https://github.com/tgstation/tgstation-server/security/advisories/GHSA-w3jx-4x93-76ph
- https://nvd.nist.gov/vuln/detail/CVE-2023-34243
- https://github.com/tgstation/tgstation-server/pull/1526
