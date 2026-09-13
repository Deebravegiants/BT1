# [M] Memory exhaustion via unbounded deserialization of keyset pagination cursors in Ash.Page.Keyset

## Summary
Severity: Medium
Advisory: CVE-2026-69659
Aliases: EEF-CVE-2026-69659, GHSA-j35q-v8h8-7mwq
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-09
Source: https://osv.dev/vulnerability/CVE-2026-69659
Type: osv

## Details
Uncontrolled Resource Consumption vulnerability in ash-project ash allows an attacker to exhaust the memory of the node via a crafted keyset pagination cursor.

Read actions with keyset pagination deserialize the client-supplied page[:after] or page[:before] cursor in decode_values/2 in lib/ash/page/keyset.ex, which base64-decodes the value and passes it to :erlang.binary_to_term/2 without bounding its size. The Erlang external term format supports zlib-compressed payloads, which the decoder inflates transparently, so a cursor of a few kilobytes can allocate tens of megabytes of heap in a single call. Ash itself only ever encodes cursors uncompressed, so the decoder accepts a term shape its encoder never produces. Concurrent requests aggregate these allocations and can terminate the node.

This issue affects ash: from 1.17.0 before 3.31.1.

## References
- https://cna.erlef.org/cves/CVE-2026-69659.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-69659
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/69xxx/CVE-2026-69659.json
- https://github.com/ash-project/ash/security/advisories/GHSA-j35q-v8h8-7mwq
- https://nvd.nist.gov/vuln/detail/CVE-2026-69659
- https://github.com/ash-project/ash/commit/1816b103af975221210478d61db20adcea700319
- https://github.com/ash-project/ash
