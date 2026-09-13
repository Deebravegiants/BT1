# [M] Header spoofing in caddy-geo-ip

## Summary
Severity: Medium
Advisory: GHSA-rxg9-hgq7-8pwx
CVE: CVE-2023-50463
CWE: CWE-290
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-12-11
Source: https://github.com/advisories/GHSA-rxg9-hgq7-8pwx
Type: github-advisory

## Affected
- Go: `github.com/shift72/caddy-geo-ip` — affected >=0

## Details
The caddy-geo-ip (aka GeoIP) middleware through 0.6.0 for Caddy 2, when trust_header X-Forwarded-For is used, allows attackers to spoof their source IP address via an X-Forwarded-For header, which may bypass a protection mechanism (trusted_proxy directive in reverse_proxy or IP address range restrictions).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-50463
- https://github.com/shift72/caddy-geo-ip/issues/4
- https://caddyserver.com/v2
- https://github.com/shift72/caddy-geo-ip/tags
- github.com/shift72/caddy-geo-ip
