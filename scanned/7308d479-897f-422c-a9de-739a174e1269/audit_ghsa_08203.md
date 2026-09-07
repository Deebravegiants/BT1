# [M] Pydantic AI: SSRF cloud-metadata blocklist bypass via IPv4-mapped IPv6 (Incomplete fix of CVE-2026-25580)

## Summary
Severity: Medium
Advisory: GHSA-cqp8-fcvh-x7r3
CVE: CVE-2026-46678
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-cqp8-fcvh-x7r3
Type: github-advisory

## Affected
- PyPI: `pydantic-ai` — affected >=1.56.0 <1.99.0
- PyPI: `pydantic-ai-slim` — affected >=1.56.0 <1.99.0

## Details
## Summary

When an application using Pydantic AI opts a URL into `force_download='allow-local'` (which disables the default block on private/internal IPs), the cloud-metadata blocklist could be bypassed by encoding the metadata IP in an IPv6 transition form (IPv4-mapped IPv6, 6to4, or NAT64). Dual-stack and translated networks route the IPv6 wrapper to the underlying IPv4 endpoint, exposing cloud IAM short-term credentials.

This is an incomplete fix of [GHSA-2jrp-274c-jhv3](https://github.com/pydantic/pydantic-ai/security/advisories/GHSA-2jrp-274c-jhv3) / [CVE-2026-25580](https://nvd.nist.gov/vuln/detail/CVE-2026-25580). The parent advisory's remediation guaranteed that "cloud metadata endpoints are always blocked, even with `allow-local`." That guarantee did not hold for IPv6-encoded forms of the metadata IPs.

## Severity

Same impact metrics as the parent CVE, but materially narrower attack surface (AC:H instead of AC:L), because exploitation requires the application to have opted into `allow-local` on a URL influenced by untrusted input.

## Who Is Affected

Applications are affected **only if** they explicitly opt for `FileUrl` (`ImageUrl`, `AudioUrl`, `VideoUrl`, `DocumentUrl`) into `force_download='allow-local'` on a URL that is, or could be, influenced by untrusted input.

Applications are **not** affected if they use any of the bundled integrations to ingest user input, because they do not propagate `force_download` from external data:

- `Agent.to_web` / `clai web`
- `VercelAIAdapter`
- `AGUIAdapter` / `Agent.to_ag_ui`

Applications that only download from developer-controlled URLs are not affected.

## Remediation

Upgrade to `1.99.0` or later. The cloud-metadata and private-IP blocklists now apply to IPv6 transition forms that route to a blocked IPv4 endpoint (IPv4-mapped IPv6, 6to4, and NAT64 well-known prefix). The blocklists have also been extended to cover additional IANA-reserved IPv4 and IPv6 special-purpose ranges.

## Workaround for Unpatched Versions

Avoid passing `force_download='allow-local'` on any URL that could be influenced by untrusted input. If developers must, resolve the hostname themselves and validate the result against their own metadata blocklist — including IPv6-encoded forms — before constructing the `FileUrl`.

## Credits

Reported by [j0hndo](mailto:dohyun4466@gmail.com).

## References
- https://github.com/pydantic/pydantic-ai/security/advisories/GHSA-2jrp-274c-jhv3
- https://github.com/pydantic/pydantic-ai/security/advisories/GHSA-cqp8-fcvh-x7r3
- https://github.com/pydantic/pydantic-ai
