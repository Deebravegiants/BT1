# [M] Wazuh: Rate Limit Bypass via /events Endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-33434
Aliases: GHSA-37qc-8242-6crg
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-33434
Type: osv

## Details
Wazuh is a free and open source platform used for threat prevention, detection, and response. In versions 4.6.0 and above, prior to 4.14.5, a logic error in CheckRateLimitsMiddleware.dispatch() causes the /events endpoint rate check to unconditionally overwrite the general rate limit result. When the global max_request_per_minute is exceeded, requests to /events still succeed if the events-specific counter (hardcoded 30/min) has not been reached. This allows event injection into analysisd beyond the admin-configured global rate limit. This issue has been fixed in version 4.14.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33434.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-37qc-8242-6crg
- https://nvd.nist.gov/vuln/detail/CVE-2026-33434
