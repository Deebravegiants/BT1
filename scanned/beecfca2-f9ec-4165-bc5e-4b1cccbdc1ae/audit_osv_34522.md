# [H] Emlog Pro is vulnerable to stored XSS attack through HTML template injection

## Summary
Severity: High
Advisory: CVE-2025-61597
Aliases: GHSA-hj97-hp2c-6m4m
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:L)
Published: 2025-10-03
Source: https://osv.dev/vulnerability/CVE-2025-61597
Type: osv

## Details
Emlog is an open source website building system. In versions 2.5.21 and below, an HTML template injection allows stored cross‑site scripting (XSS) via the mail template settings. Once a malicious payload is saved, any subsequent visit to the settings page in an authenticated admin context will execute attacker‑controlled JavaScript, enabling session/token theft and full admin account takeover. This issue is fixed in version 2.5.22.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/61xxx/CVE-2025-61597.json
- https://github.com/emlog/emlog/security/advisories/GHSA-hj97-hp2c-6m4m
- https://nvd.nist.gov/vuln/detail/CVE-2025-61597
- https://github.com/emlog/emlog/pull/179
