# [C] CVE-2020-28026

## Summary
Severity: Critical
Advisory: CVE-2020-28026
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-06
Source: https://osv.dev/vulnerability/CVE-2020-28026
Type: osv

## Details
Exim 4 before 4.94.2 has Improper Neutralization of Line Delimiters, relevant in non-default configurations that enable Delivery Status Notification (DSN). Certain uses of ORCPT= can place a newline into a spool header file, and indirectly allow unauthenticated remote attackers to execute arbitrary commands as root.

## References
- https://www.exim.org/static/doc/security/CVE-2020-qualys/CVE-2020-28026-FGETS.txt
