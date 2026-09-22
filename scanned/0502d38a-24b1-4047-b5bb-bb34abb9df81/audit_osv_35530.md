# [M] MoviePilot v2 SSRF via /api/v1/system/img/{proxy} Endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-10107
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-05-29
Source: https://osv.dev/vulnerability/CVE-2026-10107
Type: osv

## Details
MoviePilot v2 contains a server-side request forgery vulnerability in the image proxy endpoint that allows authenticated attackers to request arbitrary URLs by supplying a resource_token cookie and a URL whose domain matches the assembled allowlist. Attackers can bypass internal network protections because the SecurityUtils.is_safe_url function performs only domain-membership checking without blocking private, loopback, or link-local addresses, enabling enumeration of internal services such as Jellyfin, Emby, or Plex and exfiltration of data from internal network resources.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10107.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-10107
- https://www.vulncheck.com/advisories/moviepilot-v2-ssrf-via-api-v1-system-img-proxy-endpoint
- https://github.com/jxxghp/MoviePilot/issues/5823
- https://github.com/jxxghp/MoviePilot/commit/0b7854a0af8751160b68c43c46ded48d2bd8a212
- https://github.com/jxxghp/MoviePilot/releases/tag/v2.13.2
