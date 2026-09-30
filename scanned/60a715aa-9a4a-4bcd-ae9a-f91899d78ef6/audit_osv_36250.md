# [H] Fast DDS DDSSQLFilter Recursive Parser Stack Exhaustion (Remote DoS)

## Summary
Severity: High
Advisory: CVE-2026-22591
Aliases: GHSA-7577-rf2r-j88m
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-22591
Type: osv

## Details
eprosima Fast DDS is a C++ implementation of the DDS (Data Distribution Service) standard of the OMG (Object Management Group). Prior to versions 2.6.12, 2.14.6, 3.2.4, and 3.4.3, Fast DDS’s implementation of SQL‑based content filtering (DDSSQLFilter) allows any participant in a DDS domain to remotely crash other Fast DDS participants by sending a single crafted SEDP `DATA` submessage whose `PID_CONTENT_FILTER_PROPERTY.filterExpression` contains a deeply nested filter expression. Versions 2.6.12, 2.14.6, 3.2.4, and 3.4.3 fix the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22591.json
- https://github.com/eProsima/Fast-DDS/security/advisories/GHSA-7577-rf2r-j88m
- https://nvd.nist.gov/vuln/detail/CVE-2026-22591
