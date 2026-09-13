# [H] CVE-2020-28011

## Summary
Severity: High
Advisory: CVE-2020-28011
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-06
Source: https://osv.dev/vulnerability/CVE-2020-28011
Type: osv

## Details
Exim 4 before 4.94.2 allows Heap-based Buffer Overflow in queue_run via two sender options: -R and -S. This may cause privilege escalation from exim to root.

## References
- https://www.exim.org/static/doc/security/CVE-2020-qualys/CVE-2020-28011-SPRSS.txt
