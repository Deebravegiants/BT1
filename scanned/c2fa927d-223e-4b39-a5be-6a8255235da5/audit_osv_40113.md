# [C] Kestra: Unauthenticated Remote Code Execution via Authentication Bypass in `AuthenticationFilter`

## Summary
Severity: Critical
Advisory: CVE-2026-49869
Aliases: GHSA-5vc5-wxxq-3fjx
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-49869
Type: osv

## Details
Kestra is an open-source, event-driven orchestration platform. Prior to 1.0.45 and 1.3.21, AuthenticationFilter in Kestra OSS uses request.getPath().endsWith("/configs") to whitelist the public configuration endpoint from Basic Auth. Because the check is a suffix match rather than an exact path match, any API path whose last segment is configs bypasses authentication entirely. An unauthenticated remote attacker can exploit this to create and execute arbitrary workflows without credentials. Because Kestra ships with script execution plugins (plugin-script-shell, plugin-script-python, etc.) enabled by default, this directly results in unauthenticated Remote Code Execution as root inside the Kestra worker container.  This vulnerability is fixed in 1.0.45 and 1.3.21.

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2026-49869
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49869.json
- https://github.com/kestra-io/kestra/security/advisories/GHSA-5vc5-wxxq-3fjx
- https://nvd.nist.gov/vuln/detail/CVE-2026-49869
