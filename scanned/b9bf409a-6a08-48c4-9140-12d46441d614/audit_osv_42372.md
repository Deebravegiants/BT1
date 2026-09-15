# [C] ArcadeDB before 26.7.3 Information Disclosure via get_server_settings

## Summary
Severity: Critical
Advisory: CVE-2026-67357
Aliases: GHSA-p9wc-4fhr-78wm
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-02
Source: https://osv.dev/vulnerability/CVE-2026-67357
Type: osv

## Details
ArcadeDB versions before 26.7.3 contain an information disclosure vulnerability in the MCP get_server_settings tool that leaks the arcadedb.ha.clusterToken in cleartext. Attackers with MCP access can retrieve the cluster token and use it with X-ArcadeDB-Cluster-Token and X-ArcadeDB-Forwarded-User headers to impersonate root and achieve full server compromise.

## References
- https://github.com/ArcadeData/arcadedb/security/advisories/GHSA-p9wc-4fhr-78wm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67357.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-67357
- https://www.vulncheck.com/advisories/arcadedb-information-disclosure-via-get-server-settings
