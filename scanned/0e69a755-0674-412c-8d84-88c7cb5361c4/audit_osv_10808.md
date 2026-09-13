# [C] CVE-2017-2892

## Summary
Severity: Critical
Advisory: CVE-2017-2892
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-07
Source: https://osv.dev/vulnerability/CVE-2017-2892
Type: osv

## Details
An exploitable arbitrary memory read vulnerability exists in the MQTT packet parsing functionality of Cesanta Mongoose 6.8. A specially crafted MQTT packet can cause an arbitrary out-of-bounds memory read and write potentially resulting in information disclosure, denial of service and remote code execution. An attacker needs to send a specially crafted MQTT packet over the network to trigger this vulnerability.

## References
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2017-0399
