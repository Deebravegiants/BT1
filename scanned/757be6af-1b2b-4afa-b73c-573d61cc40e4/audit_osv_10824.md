# [H] CVE-2017-2909

## Summary
Severity: High
Advisory: CVE-2017-2909
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-11-07
Source: https://osv.dev/vulnerability/CVE-2017-2909
Type: osv

## Details
An infinite loop programming error exists in the DNS server functionality of Cesanta Mongoose 6.8 library. A specially crafted DNS request can cause an infinite loop resulting in high CPU usage and Denial Of Service. An attacker can send a packet over the network to trigger this vulnerability.

## References
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2017-0416
