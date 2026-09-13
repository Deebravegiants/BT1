# [C] CVE-2018-18765

## Summary
Severity: Critical
Advisory: CVE-2018-18765
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2018-10-29
Source: https://osv.dev/vulnerability/CVE-2018-18765
Type: osv

## Details
An exploitable arbitrary memory read vulnerability exists in the MQTT packet-parsing functionality of Cesanta Mongoose 6.13. It is a heap-based buffer over-read in mg_mqtt_next_subscribe_topic. A specially crafted MQTT SUBSCRIBE packet can cause an arbitrary out-of-bounds memory read potentially resulting in information disclosure and denial of service. An attacker needs to send a specially crafted MQTT packet over the network to trigger this vulnerability.

## References
- https://twitter.com/thracky/status/1059472674940993541
- https://github.com/TiffanyBlue/PoCbyMyself/blob/master/mongoose6.13/mqtt/Cesanta%20Mongoose%20MQTT%20mg_mqtt_next_subscribe_topic%20heap%20buffer%20overflow.md
