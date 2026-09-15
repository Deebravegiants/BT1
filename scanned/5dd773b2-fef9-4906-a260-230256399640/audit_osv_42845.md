# [C] Cypht < 2.12.2 PHP Object Injection RCE via back_query Parameter

## Summary
Severity: Critical
Advisory: CVE-2026-71981
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-71981
Type: osv

## Details
Cypht before 2.12.2 contains a PHP object injection vulnerability that allows authenticated attackers to execute arbitrary operating system commands by supplying a crafted PHP object graph in the back_query GET parameter of the logout handler. Attackers can pass a base64-encoded serialized payload through this parameter, which is decoded and passed directly to unserialize() without an allow-list, signature check, or type restriction, enabling gadget-chain exploitation to achieve remote code execution as the web server process.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71981.json
- https://github.com/cypht-org/cypht/releases/tag/v2.12.2
- https://nvd.nist.gov/vuln/detail/CVE-2026-71981
- https://www.vulncheck.com/advisories/cypht-php-object-injection-rce-via-back-query-parameter
- https://github.com/cypht-org/cypht/pull/2073
- https://github.com/cypht-org/cypht/commit/e4aa2f34e33f9328e8c93514cc3966fc3d99925e
- https://github.com/cypht-org/cypht
