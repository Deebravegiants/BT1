# [H] Fides Server-Side Request Forgery Vulnerability in Custom Integration Upload

## Summary
Severity: High
Advisory: GHSA-jq3w-9mgf-43m4
CVE: CVE-2023-46124
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2023-10-24
Source: https://github.com/advisories/GHSA-jq3w-9mgf-43m4
Type: github-advisory

## Affected
- PyPI: `ethyca-fides` — affected >=0 <2.22.1

## Details
### Impact

The Fides web application allows a custom integration to be uploaded as a ZIP file containing configuration and dataset definitions in YAML format. 

It was discovered that specially crafted YAML dataset and config files allow a malicious user to perform arbitrary requests to internal systems and exfiltrate data outside the environment (also known as a Server-Side Request Forgery). The application does not perform proper validation to block attempts to connect to internal (including localhost) resources.

Exploitation is limited to API clients with the `CONNECTOR_TEMPLATE_REGISTER` authorization scope. In the Fides Admin UI this scope is restricted to highly privileged users, specifically root users and users with the owner role.

### Patches
The vulnerability has been patched in Fides version `2.22.1`. Users are advised to upgrade to this version or later to secure their systems against this threat.

### Workarounds
There are no workarounds.

## References
- https://github.com/ethyca/fides/security/advisories/GHSA-jq3w-9mgf-43m4
- https://nvd.nist.gov/vuln/detail/CVE-2023-46124
- https://github.com/ethyca/fides/commit/cd344d016b1441662a61d0759e7913e8228ed1ee
- https://github.com/ethyca/fides
- https://github.com/ethyca/fides/releases/tag/2.22.1
