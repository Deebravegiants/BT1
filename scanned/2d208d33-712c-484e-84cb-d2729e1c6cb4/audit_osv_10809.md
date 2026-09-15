# [H] CVE-2017-2893

## Summary
Severity: High
Advisory: CVE-2017-2893
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-11-07
Source: https://osv.dev/vulnerability/CVE-2017-2893
Type: osv

## Details
An exploitable NULL pointer dereference vulnerability exists in the MQTT packet parsing functionality of Cesanta Mongoose 6.8. An MQTT SUBSCRIBE packet can cause a NULL pointer dereference leading to server crash and denial of service. An attacker needs to send a specially crafted MQTT packet over the network to trigger this vulnerability.

## References
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2017-0400
