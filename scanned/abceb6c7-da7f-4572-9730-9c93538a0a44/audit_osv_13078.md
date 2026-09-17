# [C] CVE-2018-17246

## Summary
Severity: Critical
Advisory: CVE-2018-17246
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-20
Source: https://osv.dev/vulnerability/CVE-2018-17246
Type: osv

## Details
Kibana versions before 6.4.3 and 5.6.13 contain an arbitrary file inclusion flaw in the Console plugin. An attacker with access to the Kibana Console API could send a request that will attempt to execute javascript code. This could possibly lead to an attacker executing arbitrary commands with permissions of the Kibana process on the host system.

## References
- http://www.securityfocus.com/bid/106285
- https://access.redhat.com/errata/RHBA-2018:3743
- https://discuss.elastic.co/t/elastic-stack-6-4-3-and-5-6-13-security-update/155594
- https://www.elastic.co/community/security
