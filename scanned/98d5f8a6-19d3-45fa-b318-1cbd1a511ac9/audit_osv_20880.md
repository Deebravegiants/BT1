# [H] CVE-2021-37942

## Summary
Severity: High
Advisory: CVE-2021-37942
Aliases: GHSA-5xqm-hc45-f2g2
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-11-22
Source: https://osv.dev/vulnerability/CVE-2021-37942
Type: osv

## Details
A local privilege escalation issue was found with the APM Java agent, where a user on the system could attach a malicious plugin to an application running the APM Java agent. By using this vulnerability, an attacker could execute code at a potentially higher level of permissions than their user typically has access to.

## References
- https://www.elastic.co/community/security
- https://discuss.elastic.co/t/apm-java-agent-security-update/291355
