# [C] CVE-2018-17245

## Summary
Severity: Critical
Advisory: CVE-2018-17245
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-20
Source: https://osv.dev/vulnerability/CVE-2018-17245
Type: osv

## Details
Kibana versions 4.0 to 4.6, 5.0 to 5.6.12, and 6.0 to 6.4.2 contain an error in the way authorization credentials are used when generating PDF reports. If a report requests external resources plaintext credentials are included in the HTTP request that could be recovered by an external resource provider.

## References
- https://discuss.elastic.co/t/elastic-stack-6-4-3-and-5-6-13-security-update/155594
- https://www.elastic.co/community/security
