# [H] CVE-2020-6060

## Summary
Severity: High
Advisory: CVE-2020-6060
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-02-04
Source: https://osv.dev/vulnerability/CVE-2020-6060
Type: osv

## Details
A stack buffer overflow vulnerability exists in the way MiniSNMPD version 1.4 handles multiple connections. A specially timed sequence of SNMP connections can trigger a stack overflow, resulting in a denial of service. To trigger this vulnerability, an attacker needs to simply initiate multiple connections to the server.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2019-0977
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2020-0977
