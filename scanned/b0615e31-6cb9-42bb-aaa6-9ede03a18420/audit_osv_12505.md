# [H] CVE-2018-12559

## Summary
Severity: High
Advisory: CVE-2018-12559
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-19
Source: https://osv.dev/vulnerability/CVE-2018-12559
Type: osv

## Details
An issue was discovered in the cantata-mounter D-Bus service in Cantata through 2.3.1. The mount target path check in mounter.cpp `mpOk()` is insufficient. A regular user can consequently mount a CIFS filesystem anywhere (e.g., outside of the /home directory tree) by passing directory traversal sequences such as a home/../usr substring.

## References
- https://github.com/CDrummond/cantata/commit/afc4f8315d3e96574925fb530a7004cc9e6ce3d3
- http://www.openwall.com/lists/oss-security/2018/06/18/1
