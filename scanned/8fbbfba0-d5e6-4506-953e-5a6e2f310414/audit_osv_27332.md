# [M] CVE-2024-20363

## Summary
Severity: Medium
Advisory: CVE-2024-20363
CVSS: 5.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:L/A:N)
Published: 2024-05-22
Source: https://osv.dev/vulnerability/CVE-2024-20363
Type: osv

## Details
Multiple Cisco products are affected by a vulnerability in the Snort Intrusion Prevention System (IPS) rule engine that could allow an unauthenticated, remote attacker to bypass the configured rules on an affected system. This vulnerability is due to incorrect HTTP packet handling. An attacker could exploit this vulnerability by sending crafted HTTP packets through an affected device. A successful exploit could allow the attacker to bypass configured IPS rules and allow uninspected traffic onto the network.

## References
- https://sec.cloudapps.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-snort3-ips-bypass-uE69KBMd
