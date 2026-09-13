# [H] CVE-2016-1000219

## Summary
Severity: High
Advisory: CVE-2016-1000219
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-06-16
Source: https://osv.dev/vulnerability/CVE-2016-1000219
Type: osv

## Details
Kibana before 4.5.4 and 4.1.11 when a custom output is configured for logging in, cookies and authorization headers could be written to the log files. This information could be used to hijack sessions of other users when using Kibana behind some form of authentication such as Shield.

## References
- http://www.securityfocus.com/bid/99178
- https://www.elastic.co/community/security
