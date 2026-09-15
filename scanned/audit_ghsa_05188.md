# [M] fluent-plugin-opentelemetry Has Denial of Service (DoS) via Large Payloads and Decompression Bombs in `in_opentelemetry`

## Summary
Severity: Medium
Advisory: GHSA-2jc5-xhx8-qj6h
CVE: CVE-2026-44163
CWE: CWE-770
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-2jc5-xhx8-qj6h
Type: github-advisory

## Affected
- RubyGems: `fluent-plugin-opentelemetry` — affected >=0 <0.5.3

## Details
The `fluent-plugin-opentelemetry` plugin (specifically the `in_opentelemetry` HTTP input) lacked strict size limits on incoming requests.
It was discovered that the plugin read the entire request body and decompressed payloads into memory without enforcing maximum size thresholds.

If the OpenTelemetry ingestion endpoint is exposed to untrusted networks, an attacker can send an excessively large HTTP request or a maliciously crafted, highly compressed payload.
When the plugin attempts to read or decompress this payload, it will expand to an excessive size and it will consume significant system resources.

### Impact
This vulnerability allows for a **Denial of Service (DoS)** attack via memory exhaustion. 
The rapid memory consumption during decompression can easily lead to an Out-of-Memory kill of the Fluentd process by the operating system.
This results in the disruption of all log collection and forwarding capabilities on the affected node.

### Patches
v0.5.3

### Workarounds
If an immediate upgrade is not possible, users are strongly advised to apply the following mitigations:

1. Restrict Network Access
   * Ensure that the OpenTelemetry ingestion ports (default `4318`) are deployed within a closed, trusted network. Use firewall rules (e.g., iptables, AWS Security Groups) to block access from untrusted networks or instances.
2. Use a Reverse Proxy
   * If you must expose HTTP ingestion to external sources, place a robust reverse proxy (such as Nginx) in front of Fluentd. Configure the proxy to handle the gzip decompression and enforce strict limits on both compressed and uncompressed body sizes before passing the traffic to Fluentd.

## References
- https://github.com/fluent-plugins-nursery/fluent-plugin-opentelemetry/security/advisories/GHSA-2jc5-xhx8-qj6h
- https://github.com/fluent-plugins-nursery/fluent-plugin-opentelemetry/commit/ce6c1f2a7741592c8a79afbe75fded9e8ebfa92d
- https://github.com/fluent-plugins-nursery/fluent-plugin-opentelemetry
