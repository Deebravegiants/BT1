# [H] CVE-2016-0929

## Summary
Severity: High
Advisory: CVE-2016-0929
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-09-18
Source: https://osv.dev/vulnerability/CVE-2016-0929
Type: osv

## Details
The metrics-collection component in RabbitMQ for Pivotal Cloud Foundry (PCF) 1.6.x before 1.6.4 logs command lines of failed commands, which might allow context-dependent attackers to obtain sensitive information by reading the log data, as demonstrated by a syslog message that contains credentials from a command line.

## References
- http://www.securityfocus.com/bid/91801
- https://pivotal.io/security/cve-2016-0929
