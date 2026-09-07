# [H] Fluentd is Vulnerable to Denial of Service (DoS) via Gzip Decompression Bomb in `in_http` and `in_forward`

## Summary
Severity: High
Advisory: GHSA-j9cw-hwqf-85w7
CVE: CVE-2026-44160
CWE: CWE-409
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-j9cw-hwqf-85w7
Type: github-advisory

## Affected
- RubyGems: `fluentd` — affected >=0 <1.19.3

## Details
Fluentd's `in_http` and `in_forward` plugins support receiving gzip-compressed data.
While Fluentd correctly enforces size limits on the incoming compressed payloads (e.g., via `body_size_limit` or `chunk_size_limit`), it was discovered that there is no limit enforced on the size of the decompressed data.

If a Fluentd instance is exposed to untrusted networks, an attacker can send a maliciously crafted, highly compressed payload. 
When Fluentd attempts to decompress this payload in memory, it will expand to an excessive size, completely bypassing the intended payload size limits.

### Impact
This vulnerability allows for a **Denial of Service (DoS)** attack via memory exhaustion. 
The rapid memory consumption during decompression can easily lead to an Out-of-Memory kill of the Fluentd process by the operating system.
This results in the disruption of all log collection and forwarding capabilities on the affected node.

### Patches
v1.19.3

### Workarounds
If an immediate upgrade is not possible, users are strongly advised to apply the following mitigations:

1. Restrict Network Access
   * Ensure that Fluentd input ports (such as `9880` for `in_http` and `24224` for `in_forward`) are deployed within a closed, trusted network. Use firewall rules (e.g., iptables, AWS Security Groups) to block access from untrusted networks or instances.
2. Use a Reverse Proxy
   * If developers must expose HTTP ingestion to external sources, place a robust reverse proxy (such as Nginx) in front of Fluentd. Configure the proxy to handle the gzip decompression and enforce strict limits on both compressed and uncompressed body sizes before passing the traffic to Fluentd.

## References
- https://github.com/fluent/fluentd/security/advisories/GHSA-j9cw-hwqf-85w7
- https://github.com/fluent/fluentd
- https://github.com/fluent/fluentd/releases/tag/v1.19.3
