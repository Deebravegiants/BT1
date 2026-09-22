# [C] CVE-2020-6058

## Summary
Severity: Critical
Advisory: CVE-2020-6058
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2020-02-04
Source: https://osv.dev/vulnerability/CVE-2020-6058
Type: osv

## Details
An exploitable out-of-bounds read vulnerability exists in the way MiniSNMPD version 1.4 parses incoming SNMP packets. A specially crafted SNMP request can trigger an out-of-bounds memory read, which can result in the disclosure of sensitive information and denial of service. To trigger this vulnerability, an attacker needs to send a specially crafted packet to the vulnerable server.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2020-0975
