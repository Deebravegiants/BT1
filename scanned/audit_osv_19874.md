# [M] CVE-2021-27216

## Summary
Severity: Medium
Advisory: CVE-2021-27216
CVSS: 6.3 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2021-05-06
Source: https://osv.dev/vulnerability/CVE-2021-27216
Type: osv

## Details
Exim 4 before 4.94.2 has Execution with Unnecessary Privileges. By leveraging a delete_pid_file race condition, a local user can delete arbitrary files as root. This involves the -oP and -oPX options.

## References
- https://www.exim.org/static/doc/security/CVE-2020-qualys/CVE-2020-28007-LFDIR.txt
