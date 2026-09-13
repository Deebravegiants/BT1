# [M] CVE-2019-5065

## Summary
Severity: Medium
Advisory: CVE-2019-5065
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-09-05
Source: https://osv.dev/vulnerability/CVE-2019-5065
Type: osv

## Details
An exploitable information disclosure vulnerability exists in the packet-parsing functionality of Blynk-Library v0.6.1. A specially crafted packet can cause an unterminated strncpy, resulting in information disclosure. An attacker can send a packet to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2019-0854
