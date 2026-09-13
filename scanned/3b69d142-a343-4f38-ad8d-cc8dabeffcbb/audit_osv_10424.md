# [C] CVE-2017-15535

## Summary
Severity: Critical
Advisory: CVE-2017-15535
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2017-11-01
Source: https://osv.dev/vulnerability/CVE-2017-15535
Type: osv

## Details
MongoDB 3.4.x before 3.4.10, and 3.5.x-development, has a disabled-by-default configuration setting, networkMessageCompressors (aka wire protocol compression), which exposes a vulnerability when enabled that could be exploited by a malicious attacker to deny service or modify memory.

## References
- http://www.securityfocus.com/bid/101689
- https://jira.mongodb.org/browse/SERVER-31273
