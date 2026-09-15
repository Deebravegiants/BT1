# [M] CVE-2020-28014

## Summary
Severity: Medium
Advisory: CVE-2020-28014
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:H)
Published: 2021-05-06
Source: https://osv.dev/vulnerability/CVE-2020-28014
Type: osv

## Details
Exim 4 before 4.94.2 allows Execution with Unnecessary Privileges. The -oP option is available to the exim user, and allows a denial of service because root-owned files can be overwritten.

## References
- https://www.exim.org/static/doc/security/CVE-2020-qualys/CVE-2020-28014-PIDFP.txt
