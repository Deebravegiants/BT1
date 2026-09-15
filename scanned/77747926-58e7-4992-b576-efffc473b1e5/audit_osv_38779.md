# [M] FlashMQ: Division by zero crash when using non-default deferred retained message setting

## Summary
Severity: Medium
Advisory: CVE-2026-42209
Aliases: GHSA-2789-vfcg-5922
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-42209
Type: osv

## Details
FlashMQ is a MQTT broker/server, designed for multi-CPU environments. Prior to version 1.26.1, a remote client with retained publish permission can crash the FlashMQ broker when both set_retained_message_defer_timeout and set_retained_message_defer_timeout_spread are configured to non-default values, resulting in denial of service. If anonymous retained publishing is allowed, no authentication is required; otherwise, the attacker needs the corresponding publish permission. This issue has been patched in version 1.26.1.

## References
- https://github.com/halfgaar/FlashMQ/releases/tag/v1.26.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42209.json
- https://github.com/halfgaar/FlashMQ/security/advisories/GHSA-2789-vfcg-5922
- https://nvd.nist.gov/vuln/detail/CVE-2026-42209
- https://github.com/halfgaar/FlashMQ/issues/167
- https://github.com/halfgaar/FlashMQ/commit/193b6e7767889511cfa8e933908ea5e6a1077a1f
