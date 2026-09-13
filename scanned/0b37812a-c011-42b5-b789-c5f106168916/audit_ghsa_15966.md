# [M] Unexpected visibility of environment variable configurations in @backstage/plugin-app-backend

## Summary
Severity: Medium
Advisory: GHSA-qc4v-xq2m-65wc
CVE: CVE-2024-47762
CWE: CWE-440
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2024-10-03
Source: https://github.com/advisories/GHSA-qc4v-xq2m-65wc
Type: github-advisory

## Affected
- npm: `@backstage/plugin-app-backend` — affected >=0 <0.3.75

## Details
### Impact

Configuration supplied through `APP_CONFIG_*` environment variables, for example `APP_CONFIG_backend_listen_port=7007`, where unexpectedly ignoring the visibility defined in configuration schema. This occurred even if the configuration schema specified that they should have backend or secret visibility. This was an intended feature of the `APP_CONFIG_*` way of supplying configuration, but now clearly goes against the expected behavior of the configuration system. This behavior leads to a risk of potentially exposing sensitive configuration details intended to remain private or restricted to backend processes.

### Patches

The issue has been resolved in version `0.3.75` of the `@backstage/plugin-app-backend` package. Users are encouraged to upgrade to this version to mitigate the vulnerability.

### Workarounds

As a temporary measure, avoid supplying secrets using the `APP_CONFIG_` configuration pattern. Consider alternative methods for setting secrets, such as the [environment substitution](https://backstage.io/docs/conf/writing#environment-variable-substitution) available for Backstage configuration.

### References

If you have any questions or comments about this advisory:

Open an issue in the [Backstage repository](https://github.com/backstage/backstage)
Visit our Discord, linked to in [Backstage README](https://github.com/backstage/backstage)

## References
- https://github.com/backstage/backstage/security/advisories/GHSA-qc4v-xq2m-65wc
- https://nvd.nist.gov/vuln/detail/CVE-2024-47762
- https://github.com/backstage/backstage/commit/323e6129073c5cb4cc106a1239eaec31a129554f
- https://github.com/backstage/backstage
