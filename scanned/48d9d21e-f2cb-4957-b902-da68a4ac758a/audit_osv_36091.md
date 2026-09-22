# [M] CVE-2026-20065

## Summary
Severity: Medium
Advisory: CVE-2026-20065
CVSS: 5.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:L)
Published: 2026-03-04
Source: https://osv.dev/vulnerability/CVE-2026-20065
Type: osv

## Details
Multiple Cisco products are affected by a vulnerability in the Snort 3 Detection Engine that could allow an unauthenticated, remote attacker to cause the Snort 3 Detection Engine to restart, resulting in an interruption of packet inspection.

This vulnerability is due to an error in the binder module initialization logic of the Snort Detection Engine. An attacker could exploit this vulnerability by sending certain packets through an established connection that is parsed by Snort 3. A successful exploit could allow the attacker to cause a DoS condition when the Snort 3 Detection Engine restarts unexpectedly.

## References
- https://sec.cloudapps.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-snort3-multi-dos-XFWkWSwz
