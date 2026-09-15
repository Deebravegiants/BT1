# [M] CVE-2019-2389

## Summary
Severity: Medium
Advisory: CVE-2019-2389
CVSS: 4.2 (CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-08-30
Source: https://osv.dev/vulnerability/CVE-2019-2389
Type: osv

## Details
Incorrect scoping of kill operations in MongoDB Server's packaged SysV init scripts allow users with write access to the PID file to insert arbitrary PIDs to be killed when the root user stops the MongoDB process via SysV init. This issue affects MongoDB Server v4.0 versions prior to 4.0.11; MongoDB Server v3.6 versions prior to 3.6.14; MongoDB Server v3.4 versions prior to 3.4.22.

## References
- https://jira.mongodb.org/browse/SERVER-40563
