# [C] CVE-2019-7610

## Summary
Severity: Critical
Advisory: CVE-2019-7610
CVSS: 9.0 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2019-03-25
Source: https://osv.dev/vulnerability/CVE-2019-7610
Type: osv

## Details
Kibana versions before 6.6.1 contain an arbitrary code execution flaw in the security audit logger. If a Kibana instance has the setting xpack.security.audit.enabled set to true, an attacker could send a request that will attempt to execute javascript code. This could possibly lead to an attacker executing arbitrary commands with permissions of the Kibana process on the host system.

## References
- https://access.redhat.com/errata/RHBA-2019:2824
- https://access.redhat.com/errata/RHSA-2019:2860
- https://discuss.elastic.co/t/elastic-stack-6-6-1-and-5-6-15-security-update/169077
- https://www.elastic.co/community/security
