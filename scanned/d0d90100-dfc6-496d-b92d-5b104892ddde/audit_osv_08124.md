# [H] CVE-2016-10400

## Summary
Severity: High
Advisory: CVE-2016-10400
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-07-22
Source: https://osv.dev/vulnerability/CVE-2016-10400
Type: osv

## Details
Directory Traversal exists in ATutor before 2.2.2 via the icon parameter to /mods/_core/courses/users/create_course.php. The attacker can read an arbitrary file by visiting get_course_icon.php?id= after the traversal attack.

## References
- https://github.com/atutor/ATutor/releases/tag/atutor_2_2_2
- https://www.htbridge.com/advisory/HTB23297
