# [M] CVE-2020-21055

## Summary
Severity: Medium
Advisory: CVE-2020-21055
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-05-20
Source: https://osv.dev/vulnerability/CVE-2020-21055
Type: osv

## Details
A Directory Traversal vulnerability exists in FusionPBX 4.5.7 allows malicoius users to rename any file of the system.via the (1) folder, (2) filename, and (3) newfilename variables in app\edit\filerename.php.

## References
- https://resp3ctblog.wordpress.com/2019/10/28/fusionpbx-path-traversal-6/
- https://github.com/fusionpbx/fusionpbx/commit/1a88ca61a744914d3336cc15a40fb3edbcde9085
