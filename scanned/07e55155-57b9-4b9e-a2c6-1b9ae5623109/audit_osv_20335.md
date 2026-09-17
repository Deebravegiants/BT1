# [H] CVE-2021-32816

## Summary
Severity: High
Advisory: CVE-2021-32816
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-05-14
Source: https://osv.dev/vulnerability/CVE-2021-32816
Type: osv

## Details
ProtonMail Web Client is the official AngularJS web client for the ProtonMail secure email service. ProtonMail Web Client before version 3.16.60 has a regular expression denial-of-service vulnerability. This was fixed in commit 6687fb. There is a full report available in the referenced GHSL-2021-027.

## References
- https://github.com/ProtonMail/WebClient/commit/6687fbb867ef872c96cf4fde68cb6e9c58d3fddc
- https://securitylab.github.com/advisories/GHSL-2021-027-redos-ProtonMail/
