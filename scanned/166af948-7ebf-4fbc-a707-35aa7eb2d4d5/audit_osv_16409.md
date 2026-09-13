# [C] CVE-2019-6503

## Summary
Severity: Critical
Advisory: CVE-2019-6503
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-01-22
Source: https://osv.dev/vulnerability/CVE-2019-6503
Type: osv

## Details
There is a deserialization vulnerability in Chatopera cosin v3.10.0. An attacker can execute commands during server-side deserialization by uploading maliciously constructed files. This is related to the TemplateController.java impsave method and the MainUtils toObject method.

## References
- https://github.com/chatopera/cosin/issues/177
