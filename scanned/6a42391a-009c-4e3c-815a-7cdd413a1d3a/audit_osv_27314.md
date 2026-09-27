# [C] Torrentpier 2.4.1 - RCE

## Summary
Severity: Critical
Advisory: CVE-2024-1651
Aliases: GHSA-5rwm-2xw8-hh9p
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-02-19
Source: https://osv.dev/vulnerability/CVE-2024-1651
Type: osv

## Details
Torrentpier version 2.4.1 allows executing arbitrary commands on the server.

This is possible because the application is vulnerable to insecure deserialization.

## References
- https://fluidattacks.com/advisories/xavi/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/1xxx/CVE-2024-1651.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-1651
- https://github.com/torrentpier/torrentpier
