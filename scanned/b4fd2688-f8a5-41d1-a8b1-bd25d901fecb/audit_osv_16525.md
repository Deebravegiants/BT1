# [H] CVE-2019-7620

## Summary
Severity: High
Advisory: CVE-2019-7620
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-10-30
Source: https://osv.dev/vulnerability/CVE-2019-7620
Type: osv

## Details
Logstash versions before 7.4.1 and 6.8.4 contain a denial of service flaw in the Logstash Beats input plugin. An unauthenticated user who is able to connect to the port the Logstash beats input could send a specially crafted network packet that would cause Logstash to stop responding.

## References
- https://discuss.elastic.co/t/elastic-stack-6-8-4-security-update/204908
- https://discuss.elastic.co/t/elastic-stack-7-4-1-security-update/204909
- https://www.elastic.co/community/security
