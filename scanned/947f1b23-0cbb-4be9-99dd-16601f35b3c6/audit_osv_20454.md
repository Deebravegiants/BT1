# [H] CVE-2021-33840

## Summary
Severity: High
Advisory: CVE-2021-33840
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-06-04
Source: https://osv.dev/vulnerability/CVE-2021-33840
Type: osv

## Details
The server in Luca through 1.1.14 allows remote attackers to cause a denial of service (insertion of many fake records related to COVID-19) because Phone Number data lacks a digital signature.

## References
- https://gitlab.com/lucaapp/web/-/issues/1#note_560963608
- https://luca-app.de/securityoverview/processes/guest_registration.html#verifying-the-contact-data
