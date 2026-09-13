# [M] Backstage Scaffolder plugin vulnerable to Server-Side Request Forgery

## Summary
Severity: Medium
Advisory: GHSA-qmc2-jpr5-7rg9
CVE: CVE-2024-53983
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-12-02
Source: https://github.com/advisories/GHSA-qmc2-jpr5-7rg9
Type: github-advisory

## Affected
- npm: `@backstage/plugin-scaffolder-node` — affected >=0 <0.4.12
- npm: `@backstage/plugin-scaffolder-node` — affected >=0.5.0 <0.5.1
- npm: `@backstage/plugin-scaffolder-node` — affected >=0.6.0 <0.6.1

## Details
### Impact

A vulnerability is identified in Backstage Scaffolder template functionality where Server-Side Template Injection (SSTI) can be exploited to perform Git config injection. The vulnerability allows an attacker to capture privileged git tokens used by the Backstage Scaffolder plugin. With these tokens, unauthorized access to sensitive resources in git can be achieved. The impact is considered medium severity as the Backstage Threat Model recommends restricting access to adding and editing templates in the Backstage Catalog plugin.

### Patches

The issue has been resolved in versions `v0.4.12`, `v0.5.1` and `v0.6.1` of the `@backstage/plugin-scaffolder-node` package. Users are encouraged to upgrade to this version to mitigate the vulnerability.

### Workarounds

Users can ensure that templates do not change git config.

### References

If you have any questions or comments about this advisory:

Open an issue in the [Backstage repository](https://github.com/backstage/backstage)
Visit our Discord, linked to in [Backstage README](https://github.com/backstage/backstage)

## References
- https://github.com/backstage/backstage/security/advisories/GHSA-qmc2-jpr5-7rg9
- https://nvd.nist.gov/vuln/detail/CVE-2024-53983
- https://github.com/backstage/backstage
- https://github.com/backstage/backstage/tree/master/plugins/scaffolder-node
