# [H] CVE-2017-8452

## Summary
Severity: High
Advisory: CVE-2017-8452
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-16
Source: https://osv.dev/vulnerability/CVE-2017-8452
Type: osv

## Details
Kibana versions prior to 5.2.1 configured for SSL client access, file descriptors will fail to be cleaned up after certain requests and will accumulate over time until the process crashes.

## References
- https://www.elastic.co/community/security
