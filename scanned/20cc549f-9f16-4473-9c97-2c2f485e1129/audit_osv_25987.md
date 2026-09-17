# [H] Local File Inclusion (RCE) in Cacti

## Summary
Severity: High
Advisory: CVE-2023-49084
Aliases: GHSA-pfh9-gwm6-86vp
CVSS: 8.0 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2023-12-21
Source: https://osv.dev/vulnerability/CVE-2023-49084
Type: osv

## Details
Cacti is a robust performance and fault management framework and a frontend to RRDTool - a Time Series Database (TSDB). While using the detected SQL Injection and insufficient processing of the include file path, it is possible to execute arbitrary code on the server. Exploitation of the vulnerability is possible for an authorized user. The vulnerable component is the `link.php`. Impact of the vulnerability execution of arbitrary code on the server.

## References
- http://packetstormsecurity.com/files/176995/Cacti-pollers.php-SQL-Injection-Remote-Code-Execution.html
- https://lists.debian.org/debian-lts-announce/2024/03/msg00018.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/RBEOAFKRARQHTDIYSL723XAFJ2Q6624X/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/49xxx/CVE-2023-49084.json
- https://github.com/Cacti/cacti/security/advisories/GHSA-pfh9-gwm6-86vp
- https://nvd.nist.gov/vuln/detail/CVE-2023-49084
