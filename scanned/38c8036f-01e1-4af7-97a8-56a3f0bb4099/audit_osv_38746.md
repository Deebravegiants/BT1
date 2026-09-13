# [H] Dify v1.14.1 Path Traversal via Plugin Daemon Internal API Access

## Summary
Severity: High
Advisory: CVE-2026-41948
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-05-18
Source: https://osv.dev/vulnerability/CVE-2026-41948
Type: osv

## Details
Dify version 1.14.1 and prior contain a path traversal vulnerability that allows authenticated users to manipulate requests forwarded to the Plugin Daemon's internal REST API by exploiting insufficient URL path sanitization. Attackers can traverse out of their authorized tenant path using unencoded dot sequences in task identifiers or manipulated filename parameters to access internal endpoints such as debug interfaces, requiring only knowledge of the victim tenant's UUID. NOTE: Dify Cloud allows unauthenticated free self-registration, making account creation trivially accessible to any attacker.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41948.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-41948
- https://www.vulncheck.com/advisories/dify-path-traversal-via-plugin-daemon-internal-api-access
- https://github.com/langgenius/dify/pull/35796
- https://huntr.com/bounties/35b7ad59-e35d-443f-bf77-387bfb932ec0
- https://www.zafran.io/resources/difytap-zafran-discovers-how-attackers-can-silently-wiretap-ai-data-across-tenants-on-a-platform-powering-1m-apps
