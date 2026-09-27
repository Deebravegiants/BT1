# [C] CVE-2020-28017

## Summary
Severity: Critical
Advisory: CVE-2020-28017
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-06
Source: https://osv.dev/vulnerability/CVE-2020-28017
Type: osv

## Details
Exim 4 before 4.94.2 allows Integer Overflow to Buffer Overflow in receive_add_recipient via an e-mail message with fifty million recipients. NOTE: remote exploitation may be difficult because of resource consumption.

## References
- https://www.exim.org/static/doc/security/CVE-2020-qualys/CVE-2020-28017-RCPTL.txt
