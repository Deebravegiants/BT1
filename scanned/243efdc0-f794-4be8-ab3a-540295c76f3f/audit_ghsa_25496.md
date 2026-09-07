# [C] Insecure default value for CORS configuration

## Summary
Severity: Critical
Advisory: GHSA-g27j-74fp-xfpr
CVE: CVE-2022-26969
CWE: CWE-942
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-05
Source: https://github.com/advisories/GHSA-g27j-74fp-xfpr
Type: github-advisory

## Affected
- npm: `directus` — affected >=0 <9.7.0

## Details
### Impact

The default value for the `CORS_ENABLED` and `CORS_ORIGIN` configuration was set to be very permissive by default. This could lead to unauthorized access in uncontrolled environments when the configuration hasn't been changed.

### Patches

The default values for CORS have been changed in https://github.com/directus/directus/pull/12022 which is released under 9.7.0

### Workarounds

Configure the CORS environment variables to match your project's usage, rather than leaving them at the (permissive) defaults.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [directus/directus](https://github.com/directus/directus)
* Email us at [security@directus.io](mailto:security@directus.io)

## References
- https://github.com/directus/directus/security/advisories/GHSA-g27j-74fp-xfpr
- https://nvd.nist.gov/vuln/detail/CVE-2022-26969
- https://github.com/directus/directus/pull/12022
- https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
- https://github.com/directus/directus
- https://github.com/directus/directus/blob/8daed9c41baeaf1d08c1e292bf9f0dcef65e48fb/docs/configuration/config-options.md
- https://github.com/directus/directus/releases/tag/v9.7.0
- https://security.snyk.io/vuln/SNYK-JS-DIRECTUS-2441822
