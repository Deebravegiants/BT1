# [C] Grafana OnCall 1.16.11 Unauthenticated Token Hijack via Plugin Install Endpoint

## Summary
Severity: Critical
Advisory: CVE-2026-63087
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-63087
Type: osv

## Details
Grafana OnCall through 1.16.11 contains an unauthenticated access vulnerability that allows remote attackers to obtain a valid PluginAuthToken by sending a POST request to the internal plugin install endpoint using hardcoded default stack_id and org_id values present in the public source tree. Attackers can leverage the acquired token to authenticate against all internal API endpoints, create arbitrary Admin users via the user-context header bootstrap path, revoke the legitimate plugin token, and redirect OnCall-to-Grafana API calls to an attacker-controlled host by overwriting the organization's grafana_url and api_token.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63087.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63087
- https://www.vulncheck.com/advisories/grafana-oncall-unauthenticated-token-hijack-via-plugin-install-endpoint
- https://github.com/grafana-cold-storage/oncall
- https://github.com/geo-chen/oss/blob/main/oncall.md
