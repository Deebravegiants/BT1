# [C] Convey Panel Directory Traversal in LocaleController leading to Remote Code Execution

## Summary
Severity: Critical
Advisory: CVE-2025-52562
Aliases: GHSA-43g3-qpwq-hfgg
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-06-23
Source: https://osv.dev/vulnerability/CVE-2025-52562
Type: osv

## Details
Convoy is a KVM server management panel for hosting businesses. In versions 3.9.0-rc3 to before 4.4.1, there is a directory traversal vulnerability in the LocaleController component of Performave Convoy. An unauthenticated remote attacker can exploit this vulnerability by sending a specially crafted HTTP request with malicious locale and namespace parameters. This allows the attacker to include and execute arbitrary PHP files on the server. This issue has been patched in version 4.4.1. A temporary workaround involves implementing strict Web Application Firewall (WAF) rules to incoming requests targeting the vulnerable endpoints.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/52xxx/CVE-2025-52562.json
- https://github.com/ConvoyPanel/panel/security/advisories/GHSA-43g3-qpwq-hfgg
- https://nvd.nist.gov/vuln/detail/CVE-2025-52562
- https://github.com/ConvoyPanel/panel/commit/f8d6202f3e4912b65dbd9f80ba625576944ab36c
