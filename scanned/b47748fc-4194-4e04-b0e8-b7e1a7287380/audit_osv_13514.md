# [H] CVE-2018-20145

## Summary
Severity: High
Advisory: CVE-2018-20145
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-12-13
Source: https://osv.dev/vulnerability/CVE-2018-20145
Type: osv

## Details
Eclipse Mosquitto 1.5.x before 1.5.5 allows ACL bypass: if the option per_listener_settings was set to true, and the default listener was in use, and the default listener specified an acl_file, then the acl file was being ignored.

## References
- https://github.com/eclipse/mosquitto/blob/master/ChangeLog.txt
- https://github.com/eclipse/mosquitto/commit/9097577b49b7fdcf45d30975976dd93808ccc0c4
- https://github.com/eclipse/mosquitto/issues/1073
