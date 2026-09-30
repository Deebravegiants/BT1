# [H] facileManager Privilege Escalation via Mass Assignment

## Summary
Severity: High
Advisory: CVE-2024-24573
Aliases: GHSA-w67q-pp62-j4pf
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-31
Source: https://osv.dev/vulnerability/CVE-2024-24573
Type: osv

## Details
facileManager is a modular suite of web apps built with the sysadmin in mind. In versions 4.5.0 and earlier, when a user updates their profile, a POST request containing user information is sent to the endpoint server/fm-modules/facileManager/ajax/processPost.php. It was found that non-admins can arbitrarily set their permissions and grant their non-admin accounts with super user privileges.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/24xxx/CVE-2024-24573.json
- https://github.com/WillyXJ/facileManager/security/advisories/GHSA-w67q-pp62-j4pf
- https://nvd.nist.gov/vuln/detail/CVE-2024-24573
- https://github.com/WillyXJ/facileManager/commit/0aa850d4b518f10143a4c675142b15caa5872877
