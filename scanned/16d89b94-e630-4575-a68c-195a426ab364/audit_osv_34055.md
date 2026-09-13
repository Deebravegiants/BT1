# [C] PCL Community Edition exposes login credentials in logs

## Summary
Severity: Critical
Advisory: CVE-2025-54120
Aliases: GHSA-f3rx-h3cv-696g
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-07-23
Source: https://osv.dev/vulnerability/CVE-2025-54120
Type: osv

## Details
PCL (Plain Craft Launcher) Community Edition is a Minecraft launcher. In PCL CE versions 2.12.0-beta.5 to 2.12.0-beta.9, the login credentials used during the third-party login process are accidentally recorded in the local log file. Although the log file is not automatically uploaded or shared, if the user manually sends the log file, there is a risk of leakage. This is fixed in version 2.12.0-beta.10.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54120.json
- https://github.com/PCL-Community/PCL2-CE/security/advisories/GHSA-f3rx-h3cv-696g
- https://nvd.nist.gov/vuln/detail/CVE-2025-54120
- https://github.com/PCL-Community/PCL2-CE/commit/b72eaaef05c131958b0f03bd5e7c2464bbc2af4f
