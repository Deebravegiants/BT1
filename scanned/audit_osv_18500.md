# [H] CVE-2020-28013

## Summary
Severity: High
Advisory: CVE-2020-28013
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-06
Source: https://osv.dev/vulnerability/CVE-2020-28013
Type: osv

## Details
Exim 4 before 4.94.2 allows Heap-based Buffer Overflow because it mishandles "-F '.('" on the command line, and thus may allow privilege escalation from any user to root. This occurs because of the interpretation of negative sizes in strncpy.

## References
- https://www.exim.org/static/doc/security/CVE-2020-qualys/CVE-2020-28013-PFPSN.txt
