# [H] CVE-2021-40114

## Summary
Severity: High
Advisory: CVE-2021-40114
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-10-27
Source: https://osv.dev/vulnerability/CVE-2021-40114
Type: osv

## Details
Multiple Cisco products are affected by a vulnerability in the way the Snort detection engine processes ICMP traffic that could allow an unauthenticated, remote attacker to cause a denial of service (DoS) condition on an affected device. The vulnerability is due to improper memory resource management while the Snort detection engine is processing ICMP packets. An attacker could exploit this vulnerability by sending a series of ICMP packets through an affected device. A successful exploit could allow the attacker to exhaust resources on the affected device, causing the device to reload.

## References
- https://lists.debian.org/debian-lts-announce/2023/02/msg00011.html
- https://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-snort-dos-s2R7W9UU
- https://www.debian.org/security/2023/dsa-5354
