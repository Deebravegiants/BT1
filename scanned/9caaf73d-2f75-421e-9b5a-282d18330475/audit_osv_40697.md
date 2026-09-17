# [M] MQTT-C Heap Out-of-Bounds Read and Integer Underflow in mqtt_unpack_publish_response()

## Summary
Severity: Medium
Advisory: CVE-2026-54412
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:H/SC:N/SI:N/SA:N/E:P/AU:Y/V:D)
Published: 2026-06-14
Source: https://osv.dev/vulnerability/CVE-2026-54412
Type: osv

## Details
LiamBindle MQTT-C through version 1.1.6 contains a heap-based out-of-bounds read and integer underflow in the mqtt_unpack_publish_response function in src/mqtt.c that allows a remote unauthenticated attacker controlling an MQTT broker - or able to inject MQTT traffic into an unencrypted session - to crash a subscribed MQTT-C client and potentially disclose adjacent heap memory by sending a single crafted PUBLISH packet.

## References
- https://github.com/LiamBindle/MQTT-C/blob/v1.1.6/src/mqtt.c#L1334
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54412.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-54412
- https://github.com/LiamBindle/MQTT-C
- https://cwe.mitre.org/data/definitions/125.html
- https://cwe.mitre.org/data/definitions/191.html
