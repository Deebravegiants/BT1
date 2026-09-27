# [H] CVE-2020-28008

## Summary
Severity: High
Advisory: CVE-2020-28008
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-06
Source: https://osv.dev/vulnerability/CVE-2020-28008
Type: osv

## Details
Exim 4 before 4.94.2 allows Execution with Unnecessary Privileges. Because Exim operates as root in the spool directory (owned by a non-root user), an attacker can write to a /var/spool/exim4/input spool header file, in which a crafted recipient address can indirectly lead to command execution.

## References
- https://www.exim.org/static/doc/security/CVE-2020-qualys/CVE-2020-28008-SPDIR.txt
