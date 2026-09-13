# [H] CVE-2018-9250

## Summary
Severity: High
Advisory: CVE-2018-9250
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-05-18
Source: https://osv.dev/vulnerability/CVE-2018-9250
Type: osv

## Details
interface\super\edit_list.php in OpenEMR before v5_0_1_1 allows remote authenticated users to execute arbitrary SQL commands via the newlistname parameter.

## References
- https://github.com/openemr/openemr/pull/1578
- https://github.com/openemr/openemr/commit/2a5dd0601e1f616251006d7471997ecd7aaf9651
