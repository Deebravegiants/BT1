# [C] CVE-2017-12796

## Summary
Severity: Critical
Advisory: CVE-2017-12796
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-10-23
Source: https://osv.dev/vulnerability/CVE-2017-12796
Type: osv

## Details
The Reporting Compatibility Add On before 2.0.4 for OpenMRS, as distributed in OpenMRS Reference Application before 2.6.1, does not authenticate users when deserializing XML input into ReportSchema objects. The result is that remote unauthenticated users are able to execute operating system commands by crafting malicious XML payloads, as demonstrated by a single admin/reports/reportSchemaXml.form request.

## References
- https://talk.openmrs.org/t/critical-security-advisory-2017-09-12/13291
- https://wiki.openmrs.org/display/RES/Release+Notes+2.6.1
- https://isears.github.io/jekyll/update/2017/10/21/openmrs-rce.html
