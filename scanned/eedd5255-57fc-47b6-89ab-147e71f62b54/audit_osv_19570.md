# [M] CVE-2021-22143

## Summary
Severity: Medium
Advisory: CVE-2021-22143
Aliases: GHSA-hx93-gc73-5rpr
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-11-22
Source: https://osv.dev/vulnerability/CVE-2021-22143
Type: osv

## Details
The Elastic APM .NET Agent can leak sensitive HTTP header information when logging the details during an application error. Normally, the APM agent will sanitize sensitive HTTP header details before sending the information to the APM server. During an application error it is possible the headers will not be sanitized before being sent.

## References
- https://discuss.elastic.co/t/elastic-apm-net-agent-1-10-0-security-update/274668
- https://www.elastic.co/community/security
