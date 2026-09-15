# [H] Remote Code Execution in Custom Integration Upload

## Summary
Severity: High
Advisory: GHSA-p6p2-qq95-vq5h
CVE: CVE-2023-41319
CWE: CWE-693
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-09-07
Source: https://github.com/advisories/GHSA-p6p2-qq95-vq5h
Type: github-advisory

## Affected
- PyPI: `ethyca-fides` — affected >=2.11.0 <2.19.0

## Details
### Impact
The Fides webserver API allows custom integrations to be uploaded as a ZIP file. This ZIP file must contain YAML files, but Fides can be configured to also accept the inclusion of custom Python code in it. The custom code is executed in a restricted, sandboxed environment, but the sandbox can be bypassed to execute any arbitrary code.

The vulnerability allows the execution of arbitrary code on the target system within the context of the webserver python process owner on the webserver container, which by default is `root`, and leverage that access to attack underlying infrastructure and integrated systems.

This vulnerability affects Fides versions `2.11.0` through `2.18.0`.

Exploitation is limited to API clients with the `CONNECTOR_TEMPLATE_REGISTER` authorization scope. In the Fides Admin UI this scope is restricted to highly privileged users, specifically root users and users with the owner role. 

Exploitation is only possible if the security configuration parameter `allow_custom_connector_functions` is enabled by the user deploying the Fides webserver container, either in `fides.toml` or by setting the env var `FIDES__SECURITY__ALLOW_CUSTOM_CONNECTOR_FUNCTIONS=True`. By default this configuration parameter is disabled.

### Patches
The vulnerability has been patched in Fides version `2.19.0`. Users are advised to upgrade to this version or later to secure their systems against this threat.

### Workarounds
Ensure that `allow_custom_connector_functions` in `fides.toml` and the `FIDES__SECURITY__ALLOW_CUSTOM_CONNECTOR_FUNCTIONS` are both either unset or explicit set to `False`.

## References
- https://github.com/ethyca/fides/security/advisories/GHSA-p6p2-qq95-vq5h
- https://nvd.nist.gov/vuln/detail/CVE-2023-41319
- https://github.com/ethyca/fides/commit/5989b5fa744c8d8c340963b895a054883549358a
- https://github.com/ethyca/fides
