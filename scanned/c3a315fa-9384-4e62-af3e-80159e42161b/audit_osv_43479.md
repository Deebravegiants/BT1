# [M] Wazuh 4.0.0 < 4.14.7 API DoS via Deeply Nested JSON auth_context

## Summary
Severity: Medium
Advisory: CVE-2026-74039
Aliases: GHSA-5vh8-34r8-q74q
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-74039
Type: osv

## Details
Wazuh 4.0.0 before 4.14.7 and 5.0.0-beta2 contain a denial of service vulnerability that allows authenticated attackers with allow_run_as enabled to exhaust CPU resources by submitting arbitrarily deeply nested JSON structures to the POST /security/user/authenticate/run_as endpoint. Attackers can repeatedly submit malformed auth_context bodies with unlimited nesting depth to cause the API framework to consume excessive CPU, denying service to all other API consumers.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74039.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-5vh8-34r8-q74q
- https://nvd.nist.gov/vuln/detail/CVE-2026-74039
- https://www.vulncheck.com/advisories/wazuh-api-dos-via-deeply-nested-json-auth-context
- https://github.com/wazuh/wazuh/pull/37034
- https://github.com/wazuh/wazuh
