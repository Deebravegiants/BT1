# [C] CVE-2020-6754

## Summary
Severity: Critical
Advisory: CVE-2020-6754
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-02-05
Source: https://osv.dev/vulnerability/CVE-2020-6754
Type: osv

## Details
dotCMS before 5.2.4 is vulnerable to directory traversal, leading to incorrect access control. It allows an attacker to read or execute files under $TOMCAT_HOME/webapps/ROOT/assets (which should be a protected directory). Additionally, attackers can upload temporary files (e.g., .jsp files) into /webapps/ROOT/assets/tmp_upload, which can lead to remote command execution (with the permissions of the user running the dotCMS application).

## References
- https://dotcms.com/security/SI-54
- https://github.com/dotCMS/core/issues/17796
