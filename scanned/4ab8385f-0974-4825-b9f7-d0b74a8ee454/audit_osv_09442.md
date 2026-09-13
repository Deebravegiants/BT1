# [H] CVE-2016-9882

## Summary
Severity: High
Advisory: CVE-2016-9882
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-01-13
Source: https://osv.dev/vulnerability/CVE-2016-9882
Type: osv

## Details
An issue was discovered in Cloud Foundry Foundation cf-release versions prior to v250 and CAPI-release versions prior to v1.12.0. Cloud Foundry logs the credentials returned from service brokers in Cloud Controller system component logs. These logs are written to disk and often sent to a log aggregator via syslog.

## References
- http://www.securityfocus.com/bid/95441
- https://www.cloudfoundry.org/cve-2016-9882/
