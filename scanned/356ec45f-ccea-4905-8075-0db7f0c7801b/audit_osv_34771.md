# [M] grist-core has path to server-side requests via websocket

## Summary
Severity: Medium
Advisory: CVE-2025-64752
Aliases: GHSA-qh95-2qv8-pqx3
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2025-11-13
Source: https://osv.dev/vulnerability/CVE-2025-64752
Type: osv

## Details
grist-core is a spreadsheet hosting server. Prior to version 1.7.7, a user with access to any document on a Grist installation can use a feature for fetching from a URL that is executed on the server. The privileged network access of server-side requests could offer opportunities for attack escalation. This issue is fixed in version 1.7.7. The mitigation was to use the proxy for untrusted fetches intended for such purposes. As a workaround, avoid making http/https endpoints available to an instance running Grist that expose credentials or operate without credentials.

## References
- https://github.com/gristlabs/grist-core/releases/tag/v1.7.7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64752.json
- https://github.com/gristlabs/grist-core/security/advisories/GHSA-qh95-2qv8-pqx3
- https://nvd.nist.gov/vuln/detail/CVE-2025-64752
