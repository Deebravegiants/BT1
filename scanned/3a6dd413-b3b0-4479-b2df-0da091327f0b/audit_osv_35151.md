# [M] NanoMQ $share/ Subscription Validation and Forwarding Parsing Inconsistency: NULL Pointer Increment Causes Crash

## Summary
Severity: Medium
Advisory: CVE-2025-68699
Aliases: GHSA-qv5f-c6v2-2f8h
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-02-04
Source: https://osv.dev/vulnerability/CVE-2025-68699
Type: osv

## Details
NanoMQ MQTT Broker (NanoMQ) is an all-around Edge Messaging Platform. In version 0.24.6, NanoMQ has a protocol parsing / forwarding inconsistency when handling shared subscriptions ($share/). A malformed SUBSCRIBE topic such as $share/ab (missing the second /) is not strictly validated during the subscription stage, so the invalid Topic Filter is stored into the subscription table. Later, when any PUBLISH matches this subscription, the broker send path (nmq_pipe_send_start_v4/v5) performs a second $share/ parsing using strchr() and increments the returned pointer without NULL checks. If the second strchr() returns NULL, sub_topic++ turns the pointer into an invalid address (e.g. 0x1). This invalid pointer is then passed into topic_filtern(), which triggers strlen() and crashes with SIGSEGV. The crash is stable and remotely triggerable. This issue has been patched in version 0.24.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68699.json
- https://github.com/nanomq/nanomq/security/advisories/GHSA-qv5f-c6v2-2f8h
- https://nvd.nist.gov/vuln/detail/CVE-2025-68699
- https://github.com/nanomq/nanomq/commit/89d68d678e7f841ae7baa45cba8d9bc7ddc9ef4b
