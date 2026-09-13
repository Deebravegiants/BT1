# [M] Dataease before 1.11.2 access control issue allows attackers to arbitrarily uninstall plugin

## Summary
Severity: Medium
Advisory: GHSA-c2pj-rr68-pw94
CVE: CVE-2022-34112
CWE: CWE-732
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-07-23
Source: https://github.com/advisories/GHSA-c2pj-rr68-pw94
Type: github-advisory

## Affected
- Maven: `io.dataease:dataease-plugin-common` — affected >=0 <1.11.2

## Details
An access control issue in the component /api/plugin/uninstall Dataease v1.11.1 allows attackers to arbitrarily uninstall the plugin, a right normally reserved for the administrator. Version 1.11.2 contains a patch for this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34112
- https://github.com/dataease/dataease/issues/2429
- https://github.com/dataease/dataease/commit/5f611d3e3934816e9ad34e3d21807978001e2c8b
- https://github.com/dataease/dataease
- https://github.com/dataease/dataease/releases/tag/v1.11.2
