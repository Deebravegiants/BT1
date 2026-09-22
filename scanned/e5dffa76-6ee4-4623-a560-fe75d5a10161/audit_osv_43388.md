# [M] Serendipity before 2.6.0 SSRF via hex IPv4 and IPv6 addresses

## Summary
Severity: Medium
Advisory: CVE-2026-73629
Aliases: GHSA-2m48-gjj5-5x86
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:H/SI:L/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-73629
Type: osv

## Details
Serendipity before 2.6.0 contains a server-side request forgery vulnerability in the serendipity_url_allowed() filter that fails to block hex-encoded IPv4 addresses, IPv6 literals, and link-local ranges. Authenticated users with adminImagesAdd permission can bypass the filter using alternate address formats to request internal services and retrieve response bodies through the public uploads directory.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73629.json
- https://github.com/s9y/Serendipity/security/advisories/GHSA-2m48-gjj5-5x86
- https://nvd.nist.gov/vuln/detail/CVE-2026-73629
- https://www.vulncheck.com/advisories/serendipity-before-ssrf-via-hex-ipv4-and-ipv6-addresses
