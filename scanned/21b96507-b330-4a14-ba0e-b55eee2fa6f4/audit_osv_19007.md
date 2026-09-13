# [H] CVE-2020-6059

## Summary
Severity: High
Advisory: CVE-2020-6059
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2020-02-04
Source: https://osv.dev/vulnerability/CVE-2020-6059
Type: osv

## Details
An exploitable out of bounds read vulnerability exists in the way MiniSNMPD version 1.4 parses incoming SNMP packets. A specially crafted SNMP request can trigger an out of bounds memory read which can result in sensitive information disclosure and Denial Of Service. In order to trigger this vulnerability, an attacker needs to send a specially crafted packet to the vulnerable server.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2019-0976
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2020-0976
