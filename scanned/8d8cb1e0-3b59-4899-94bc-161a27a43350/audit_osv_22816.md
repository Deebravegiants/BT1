# [C] Database log access in ZoneMinder

## Summary
Severity: Critical
Advisory: CVE-2022-39289
Aliases: GHSA-mpcx-3gvh-9488
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2022-10-07
Source: https://osv.dev/vulnerability/CVE-2022-39289
Type: osv

## Details
ZoneMinder is a free, open source Closed-circuit television software application. In affected versions the ZoneMinder API Exposes Database Log contents to user without privileges, allows insertion, modification, deletion of logs without System Privileges. Users are advised yo upgrade as soon as possible. Users unable to upgrade should disable database logging.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39289.json
- https://github.com/ZoneMinder/zoneminder/security/advisories/GHSA-mpcx-3gvh-9488
- https://nvd.nist.gov/vuln/detail/CVE-2022-39289
- https://github.com/ZoneMinder/zoneminder/commit/34ffd92bf123070cab6c83ad4cfe6297dd0ed0b4
