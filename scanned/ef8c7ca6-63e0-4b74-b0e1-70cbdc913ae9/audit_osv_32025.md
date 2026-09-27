# [C] Cacti has Authenticated RCE via multi-line SNMP responses

## Summary
Severity: Critical
Advisory: CVE-2025-22604
Aliases: GHSA-c5j8-jxj3-hh36
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-01-27
Source: https://osv.dev/vulnerability/CVE-2025-22604
Type: osv

## Details
Cacti is an open source performance and fault management framework. Due to a flaw in multi-line SNMP result parser, authenticated users can inject malformed OIDs in the response. When processed by ss_net_snmp_disk_io() or ss_net_snmp_disk_bytes(), a part of each OID will be used as a key in an array that is used as part of a system command, causing a command execution vulnerability. This vulnerability is fixed in 1.2.29.

## References
- https://lists.debian.org/debian-lts-announce/2025/02/msg00010.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22604.json
- https://github.com/Cacti/cacti/security/advisories/GHSA-c5j8-jxj3-hh36
- https://nvd.nist.gov/vuln/detail/CVE-2025-22604
- https://github.com/Cacti/cacti/commit/c7e4ee798d263a3209ae6e7ba182c7b65284d8f0
