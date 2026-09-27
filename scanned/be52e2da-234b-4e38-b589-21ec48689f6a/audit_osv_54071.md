# [H] CVE-2023-38060

## Summary
Severity: High
Advisory: CVE-2023-38060
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-07-24
Source: https://osv.dev/vulnerability/CVE-2023-38060
Type: osv

## Details
Improper Input Validation vulnerability in the ContentType parameter for attachments on TicketCreate or TicketUpdate operations of the OTRS Generic Interface modules allows  any authenticated attacker to  to perform an host header injection for the ContentType header of the attachment. 


This issue affects OTRS: from 7.0.X before 7.0.45, from 8.0.X before 8.0.35; ((OTRS)) Community Edition: from 6.0.1 through 6.0.34.

## References
- https://lists.debian.org/debian-lts-announce/2023/08/msg00040.html
- https://otrs.com/release-notes/otrs-security-advisory-2023-04/
