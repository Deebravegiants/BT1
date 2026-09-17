# [M] alf.io's preloaded data as json is not escaped correctly

## Summary
Severity: Medium
Advisory: CVE-2024-45299
Aliases: GHSA-mcx6-25f8-8rqw
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:H)
Published: 2024-09-06
Source: https://osv.dev/vulnerability/CVE-2024-45299
Type: osv

## Details
alf.io is an open source ticket reservation system for conferences, trade shows, workshops, and meetups. Prior to version 2.0-M5, the preloaded data as json is not escaped correctly, the administrator / event admin could break their own install by inserting non correctly escaped text. The Content-Security-Policy directive blocks any potential script execution. The administrator or event administrator can override the texts for customization purpose. The texts are not properly escaped. Version 2.0-M5 fixes this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45299.json
- https://github.com/alfio-event/alf.io/security/advisories/GHSA-mcx6-25f8-8rqw
- https://nvd.nist.gov/vuln/detail/CVE-2024-45299
- https://github.com/alfio-event/alf.io/commit/e7131c588f4ac31067a41d0e31e6a6a721b2ff4b
