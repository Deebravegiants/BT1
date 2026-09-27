# [M] NanoMQ UAF of retain message due to invalid MQTTV5 properties

## Summary
Severity: Medium
Advisory: CVE-2025-65953
Aliases: GHSA-r95p-wjm8-2qxr
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:L)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/CVE-2025-65953
Type: osv

## Details
NanoMQ MQTT Broker (NanoMQ) is an all-around Edge Messaging Platform. Prior to version 0.22.5, a Heap-Use-After-Free (UAF) vulnerability exists in the TCP transport component of NanoMQ, which relies on the underlying NanoNNG library (specifically in src/sp/transport/mqtt/broker_tcp.c). The vulnerability is due to improper resource management and premature cleanup of message and pipe structures under specific malformed MQTTV5 retain message traffic conditions. This issue has been patched in version 0.22.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65953.json
- https://github.com/nanomq/nanomq/security/advisories/GHSA-r95p-wjm8-2qxr
- https://nvd.nist.gov/vuln/detail/CVE-2025-65953
