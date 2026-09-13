# [H] CVE-2020-28007

## Summary
Severity: High
Advisory: CVE-2020-28007
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-06
Source: https://osv.dev/vulnerability/CVE-2020-28007
Type: osv

## Details
Exim 4 before 4.94.2 allows Execution with Unnecessary Privileges. Because Exim operates as root in the log directory (owned by a non-root user), a symlink or hard link attack allows overwriting critical root-owned files anywhere on the filesystem.

## References
- https://www.exim.org/static/doc/security/CVE-2020-qualys/CVE-2020-28007-LFDIR.txt
