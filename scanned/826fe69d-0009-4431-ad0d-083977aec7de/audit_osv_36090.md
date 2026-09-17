# [M] CVE-2026-20058

## Summary
Severity: Medium
Advisory: CVE-2026-20058
CVSS: 5.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:L)
Published: 2026-03-04
Source: https://osv.dev/vulnerability/CVE-2026-20058
Type: osv

## Details
Multiple Cisco products are affected by vulnerabilities in the Snort 3 VBA feature that could allow an unauthenticated, remote attacker to cause the Snort 3 Detection Engine to crash.

These vulnerabilities are due to improper error checking when decompressing VBA data. An attacker could exploit these vulnerabilities by sending crafted VBA data to the Snort 3 Detection Engine on the targeted device. A successful exploit could allow the attacker to cause the Snort 3 Detection Engine to unexpectedly restart, causing a DoS condition.

## References
- https://sec.cloudapps.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-ftd-snort3-vbavuls-96UcVVed
