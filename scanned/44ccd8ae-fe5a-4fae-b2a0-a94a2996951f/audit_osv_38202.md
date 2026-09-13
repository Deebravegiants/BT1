# [M] NanoMQ Incorrectly Accepts a Malformed SUBSCRIBE and Can Be Driven into an ASAN-Detectable Out-of-Bounds Read

## Summary
Severity: Medium
Advisory: CVE-2026-35217
Aliases: GHSA-w4xh-p384-w556
CVSS: 6.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-35217
Type: osv

## Details
NanoMQ contains a protocol-semantics flaw in its MQTT v5 `SUBSCRIBE` handling: if a subscription entry is missing the final 1-byte `Subscription Options` field, the broker may still accept the malformed packet and install the subscription into internal broker state. Under a specific packet-length construction, the same parser flaw also causes a 1-byte out-of-bounds read that crosses the real heap allocation boundary and is detected by ASAN as a `heap-buffer-overflow`.

If the consumed byte happens to look acceptable, NanoMQ may continue and append the malformed subscription entry into its internal `subinfol` state. In that case, a `SUBSCRIBE` packet that should be rejected by MQTT rules is instead treated as a successful subscription. Whether ASAN reports the bug does not depend on MQTT's logical `remain` boundary; it depends on whether the read crosses the real heap allocation boundary of the underlying message buffer. In other words, these are not two unrelated issues. They are two manifestations of the same parsing defect: by default, it appears as a semantic vulnerability, and under suitable input conditions, it also becomes a verifiable out-of-bounds read vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35217.json
- https://github.com/nanomq/nanomq/security/advisories/GHSA-w4xh-p384-w556
- https://nvd.nist.gov/vuln/detail/CVE-2026-35217
