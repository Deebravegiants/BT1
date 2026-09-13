# [M] Traefik before v2.11.55 and v3.0.0 through v3.7.10 mTLS Bypass via TLS Option Conflict

## Summary
Severity: Medium
Advisory: CVE-2026-85597
Aliases: GHSA-g55h-rg46-x9c5
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85597
Type: osv

## Details
Traefik before v2.11.55 and v3.0.0 through v3.7.10 contain a TLS option conflict resolution vulnerability that allows unauthenticated attackers to bypass client-certificate authentication by creating conflicting TLS options on multi-host routers. Attackers can reach protected backends by exploiting shared TLS resolution across multiple hostnames in a single router rule, causing the strict mTLS requirement to fall back to default options for all hosts.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85597.json
- https://github.com/traefik/traefik/security/advisories/GHSA-g55h-rg46-x9c5
- https://nvd.nist.gov/vuln/detail/CVE-2026-85597
- https://www.vulncheck.com/advisories/traefik-before-2.11.55-mtls-bypass-via-tls-option-conflict
