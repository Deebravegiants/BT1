# [H] CVE-2018-20226

## Summary
Severity: High
Advisory: CVE-2018-20226
CVSS: 7.2 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-21
Source: https://osv.dev/vulnerability/CVE-2018-20226
Type: osv

## Details
An organization administrator can add a super administrator in THEHIVE PROJECT Cortex before 2.1.3 due to the lack of overriding the Role.toString method.

## References
- https://github.com/TheHive-Project/Cortex/blob/2.1.3/CHANGELOG.md
- https://github.com/TheHive-Project/Cortex/commit/1aaf2182a6b722ad539e2717bc11967d1bde723a
- https://github.com/TheHive-Project/Cortex/issues/158
