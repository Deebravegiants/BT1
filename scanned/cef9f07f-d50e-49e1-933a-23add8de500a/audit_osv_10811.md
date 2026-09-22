# [H] CVE-2017-2895

## Summary
Severity: High
Advisory: CVE-2017-2895
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2017-11-07
Source: https://osv.dev/vulnerability/CVE-2017-2895
Type: osv

## Details
An exploitable arbitrary memory read vulnerability exists in the MQTT packet parsing functionality of Cesanta Mongoose 6.8. A specially crafted MQTT SUBSCRIBE packet can cause an arbitrary out-of-bounds memory read potentially resulting in information disclosure and denial of service. An attacker needs to send a specially crafted MQTT packet over the network to trigger this vulnerability.

## References
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2017-0402
