# [M] twenty-server SSRF protection bypass via IPv4-mapped IPv6 address normalization

## Summary
Severity: Medium
Advisory: CVE-2026-33975
Aliases: GHSA-vrcj-hv2q-c58m
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-05-05
Source: https://osv.dev/vulnerability/CVE-2026-33975
Type: osv

## Details
Twenty is an open source CRM built with NestJS (Node.js). In versions 1.18.0 and earlier, the SSRF protection in twenty-server's SecureHttpClientService can be bypassed using IPv4-mapped IPv6 addresses in URL IP literals. Node.js's URL parser normalizes IPv4-mapped IPv6 addresses to compressed hex form (e.g., ::ffff:169.254.169.254 becomes ::ffff:a9fe:a9fe), but the isPrivateIp utility only recognizes the dotted-decimal notation. As a result, the hex form passes the SSRF check unchecked. Additionally, the socket lookup validation event does not fire for IP literal addresses, bypassing the second validation layer. An authenticated user can reach any internal IP, including cloud metadata endpoints, to exfiltrate credentials such as IAM keys.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33975.json
- https://github.com/twentyhq/twenty/security/advisories/GHSA-vrcj-hv2q-c58m
- https://nvd.nist.gov/vuln/detail/CVE-2026-33975
