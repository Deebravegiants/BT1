# [M] CVE-2021-43403

## Summary
Severity: Medium
Advisory: CVE-2021-43403
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-09-29
Source: https://osv.dev/vulnerability/CVE-2021-43403
Type: osv

## Details
An issue was discovered in FusionPBX before 4.5.30. The log_viewer.php Log View page allows an authenticated user to choose an arbitrary filename for download (i.e., not necessarily freeswitch.log in the intended directory).

## References
- https://github.com/fusionpbx/fusionpbx/commit/57b7bf0d6b67bda07d550b07d984a44755510d9c
