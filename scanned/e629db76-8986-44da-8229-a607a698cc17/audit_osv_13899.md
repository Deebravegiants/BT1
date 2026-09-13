# [C] CVE-2018-3972

## Summary
Severity: Critical
Advisory: CVE-2018-3972
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-09-26
Source: https://osv.dev/vulnerability/CVE-2018-3972
Type: osv

## Details
An exploitable code execution vulnerability exists in the Levin deserialization functionality of the Epee library, as used in Monero 'Lithium Luna' (v0.12.2.0-master-ffab6700) and other cryptocurrencies. A specially crafted network packet can cause a logic flaw, resulting in code execution. An attacker can send a packet to trigger this vulnerability.

## References
- https://blog.talosintelligence.com/2018/09/epee-levin-vuln.html
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2018-0637
