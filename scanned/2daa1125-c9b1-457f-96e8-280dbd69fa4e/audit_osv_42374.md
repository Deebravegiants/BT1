# [M] Linuxfabrik monitoring-plugins: SSRF and auth-token disclosure via unvalidated @odata.id link in redfish-* plugins

## Summary
Severity: Medium
Advisory: CVE-2026-67436
Aliases: GHSA-96fx-pqc3-28xv
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-29
Source: https://osv.dev/vulnerability/CVE-2026-67436
Type: osv

## Details
Linuxfabrik monitoring-plugins provides Python monitoring plugins for Icinga, Nagios, and related monitoring systems. In 6.0.0 and earlier, the redfish-* plugins built request URLs by concatenating an operator-supplied base URL with response-supplied @odata.id links, allowing a malicious or compromised BMC to redirect authenticated Redfish requests and disclose X-Auth-Token or HTTP Basic credentials.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67436.json
- https://github.com/Linuxfabrik/monitoring-plugins/security/advisories/GHSA-96fx-pqc3-28xv
- https://nvd.nist.gov/vuln/detail/CVE-2026-67436
- https://github.com/Linuxfabrik/monitoring-plugins/commit/ffb0a81308cbfc018da857a89e0d07a67bf89fc3
