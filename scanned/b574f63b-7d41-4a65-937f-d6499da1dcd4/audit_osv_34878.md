# [M] NanoMQ has Use-After-Free of malformed bridging message

## Summary
Severity: Medium
Advisory: CVE-2025-66023
Aliases: GHSA-24f7-q5hh-27hf
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:H/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H)
Published: 2026-01-01
Source: https://osv.dev/vulnerability/CVE-2025-66023
Type: osv

## Details
NanoMQ MQTT Broker (NanoMQ) is an all-around Edge Messaging Platform. Versions prior to 0.24.5 have a Heap-Use-After-Free (UAF) vulnerability within the MQTT bridge client component (implemented via the underlying NanoNNG library). The vulnerability is triggered when NanoMQ acts as a bridge connecting to a remote MQTT broker. A malicious remote broker can trigger a crash (Denial of Service) or potential memory corruption by accepting the connection and immediately sending a malformed packet sequence. Version 0.34.5 contains a patch. The patch enforces stricter protocol adherence in the MQTT client SDK embedded in NanoMQ. Specifically, it ensures that CONNACK is always the first packet processed in the line. This prevents the state confusion that led to the Heap-Use-After-Free (UAF) when a malicious server sent a malformed packet sequence immediately after connection establishment. As a workaround, validate the remote broker before bridging.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66023.json
- https://github.com/nanomq/nanomq/security/advisories/GHSA-24f7-q5hh-27hf
- https://nvd.nist.gov/vuln/detail/CVE-2025-66023
- https://github.com/nanomq/nanomq/issues/2145
- https://github.com/nanomq/NanoNNG/pull/1365
