# [M] Cortex's Alertmanager can expose local files content via specially crafted config

## Summary
Severity: Medium
Advisory: GHSA-cq2g-pw6q-hf7j
CVE: CVE-2022-23536
CWE: CWE-184, CWE-641, CWE-73
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-12-19
Source: https://github.com/advisories/GHSA-cq2g-pw6q-hf7j
Type: github-advisory

## Affected
- Go: `github.com/cortexproject/cortex` — affected >=1.14.0 <1.14.1
- Go: `github.com/cortexproject/cortex` — affected >=1.13.0 <1.13.2

## Details
### Impact

A local file inclusion vulnerability exists in Cortex versions v1.13.0, v1.13.1 and v1.14.0, where a malicious actor could remotely read local files as a result of parsing maliciously crafted Alertmanager configurations when submitted to the [Alertmanager Set Configuration API](https://cortexmetrics.io/docs/api/#set-alertmanager-configuration). Only users of the Cortex Alertmanager service using `-experimental.alertmanager.enable-api` or `enable_api: true` are affected.

### Specific Go Packages Affected
github.com/cortexproject/cortex/pkg/alertmanager

### Patches
Affected Cortex users are advised to upgrade to versions 1.13.2 or 1.14.1.

### Workarounds
Patching is ultimately advised. Using out-of-bound validation, Cortex administrators may reject Alertmanager configurations containing the `api_key_file` setting in the `opsgenie_configs` section and `opsgenie_api_key_file` in the `global` section before sending to the [Set Alertmanager Configuration API](https://cortexmetrics.io/docs/api/#set-alertmanager-configuration) as a workaround.

### References
- Fixed Versions:
   - https://github.com/cortexproject/cortex/releases/tag/v1.14.1
   - https://github.com/cortexproject/cortex/releases/tag/v1.13.2
- https://cortexmetrics.io/docs/api/#set-alertmanager-configuration

### For more information
If you have any questions or comments about this advisory:

* Open an issue in [cortex](https://github.com/cortexproject/cortex/issues/new/choose)
* Email us at [cortex-team@googlegroups.com](mailto:cortex-team@googlegroups.com).

## References
- https://github.com/cortexproject/cortex/security/advisories/GHSA-cq2g-pw6q-hf7j
- https://nvd.nist.gov/vuln/detail/CVE-2022-23536
- https://github.com/cortexproject/cortex/commit/03e023d8b012887b31cc268d0d011b01e1e65506
- https://cortexmetrics.io/docs/api/#set-alertmanager-configuration
- https://github.com/cortexproject/cortex
- https://github.com/cortexproject/cortex/releases/tag/v1.13.2
- https://github.com/cortexproject/cortex/releases/tag/v1.14.1
- https://pkg.go.dev/vuln/GO-2022-1175
