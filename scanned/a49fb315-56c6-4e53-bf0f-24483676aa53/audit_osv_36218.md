# [M] NanoMQ 0.24.6 Use-After-Free Leading to Heap Corruption and Broker Crash

## Summary
Severity: Medium
Advisory: CVE-2026-22040
Aliases: GHSA-v57q-w88m-424r
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-03-04
Source: https://osv.dev/vulnerability/CVE-2026-22040
Type: osv

## Details
NanoMQ MQTT Broker (NanoMQ) is an all-around Edge Messaging Platform. In version 0.24.6, by generating a combined traffic pattern of high-frequency publishes and rapid reconnect/kick-out using the same ClientID and massive subscribe/unsubscribe jitter, it is possible to reliably trigger heap memory corruption in the Broker process, causing it to exit immediately with SIGABRT due to free(): invalid pointer. As of time of publication, no known patched versions are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22040.json
- https://github.com/nanomq/nanomq/security/advisories/GHSA-v57q-w88m-424r
- https://nvd.nist.gov/vuln/detail/CVE-2026-22040
