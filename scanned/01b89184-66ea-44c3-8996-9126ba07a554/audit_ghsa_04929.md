# [H] Crawl4AI: SSRF filter bypass in Docker server via IPv6 transition forms (NAT64 / 6to4 / unspecified / v4-mapped)

## Summary
Severity: High
Advisory: GHSA-4qqr-vv2q-cmr5
CVE: CVE-2026-53754
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-4qqr-vv2q-cmr5
Type: github-advisory

## Affected
- PyPI: `crawl4ai` — affected >=0 <0.8.8

## Details
### Summary

The Docker API server's SSRF protection (`validate_webhook_url` / `validate_url_destination` in `deploy/docker/utils.py`) used an explicit IPv4/IPv6 CIDR blocklist that missed several address families. An attacker could reach internal services and cloud metadata endpoints (e.g. `169.254.169.254`) despite the filter by encoding an internal IPv4 address inside an IPv6 transition form, or by using the IPv6 unspecified address.

Because the Docker API is unauthenticated by default (`jwt_enabled: false`), no credentials are required.

### Affected paths

The blocklist was applied to crawl URLs (`POST /crawl`, `/md`, `/html`, `/screenshot`, `/pdf`, `/execute_js`) and webhook URLs (`/crawl/job`, `/llm/job`). All shared the same incomplete check.

### Bypasses

The following all resolve to (or route to) blocked internal addresses but were NOT caught:
- IPv6 unspecified `::`
- NAT64 `64:ff9b::a9fe:a9fe` (embeds `169.254.169.254`)
- 6to4 `2002:a9fe:a9fe::` (embeds `169.254.169.254`)
- IPv4-mapped `::ffff:169.254.169.254`
- IPv4-compatible `::a9fe:a9fe`

The error message also echoed the resolved internal IP, acting as a minor DNS/oracle leak.

### Impact

Server-Side Request Forgery: an unauthenticated attacker can make the server fetch internal-network URLs and cloud instance-metadata endpoints, potentially exposing internal services and cloud credentials.

### Fix

The blocklist is replaced by a single rule: reject any resolved IP where `not ip.is_global`, evaluated on the address AND every embedded IPv4 transition form (v4-mapped, NAT64 `64:ff9b::/96`, 6to4 `2002::/16`, v4-compat `::/96`). Error messages are now opaque and no longer echo the resolved IP.

### Workarounds

- Upgrade to the patched version.
- Enable authentication (`CRAWL4AI_API_TOKEN`).
- Restrict the container's outbound network access (egress firewall / no metadata route).

### Credits

Internal security audit (Crawl4AI maintainers).

## References
- https://github.com/unclecode/crawl4ai/security/advisories/GHSA-4qqr-vv2q-cmr5
- https://nvd.nist.gov/vuln/detail/CVE-2026-53754
- https://github.com/pypa/advisory-database/tree/main/vulns/crawl4ai/PYSEC-2026-587.yaml
- https://github.com/unclecode/crawl4ai
