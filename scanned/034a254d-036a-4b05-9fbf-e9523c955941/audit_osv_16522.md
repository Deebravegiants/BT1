# [C] CVE-2019-7612

## Summary
Severity: Critical
Advisory: CVE-2019-7612
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-03-25
Source: https://osv.dev/vulnerability/CVE-2019-7612
Type: osv

## Details
A sensitive data disclosure flaw was found in the way Logstash versions before 5.6.15 and 6.6.1 logs malformed URLs. If a malformed URL is specified as part of the Logstash configuration, the credentials for the URL could be inadvertently logged as part of the error message.

## References
- https://discuss.elastic.co/t/elastic-stack-6-6-1-and-5-6-15-security-update/169077
- https://security.netapp.com/advisory/ntap-20190411-0002/
- https://www.elastic.co/community/security
