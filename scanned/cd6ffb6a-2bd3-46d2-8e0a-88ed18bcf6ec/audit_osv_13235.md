# [C] CVE-2018-18764

## Summary
Severity: Critical
Advisory: CVE-2018-18764
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2018-10-29
Source: https://osv.dev/vulnerability/CVE-2018-18764
Type: osv

## Details
An exploitable arbitrary memory read vulnerability exists in the MQTT packet-parsing functionality of Cesanta Mongoose 6.13. It is a heap-based buffer over-read in a parse_mqtt getu16 call. A specially crafted MQTT SUBSCRIBE packet can cause an arbitrary out-of-bounds memory read potentially resulting in information disclosure and denial of service. An attacker needs to send a specially crafted MQTT packet over the network to trigger this vulnerability.

## References
- https://github.com/TiffanyBlue/PoCbyMyself/blob/master/mongoose6.13/mqtt/Cesanta%20Mongoose%20MQTT%20getu16%20heap%20buffer%20overflow1.md
- https://github.com/TiffanyBlue/PoCbyMyself/blob/master/mongoose6.13/mqtt/Cesanta%20Mongoose%20MQTT%20getu16%20heap%20buffer%20overflow2.md
