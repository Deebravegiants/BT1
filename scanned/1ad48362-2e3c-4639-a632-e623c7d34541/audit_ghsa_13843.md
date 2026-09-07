# [M] Cross site scripting Vulnerability in backstage Software Catalog

## Summary
Severity: Medium
Advisory: GHSA-7hv8-3fr9-j2hv
CVE: CVE-2023-25571
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2023-02-14
Source: https://github.com/advisories/GHSA-7hv8-3fr9-j2hv
Type: github-advisory

## Affected
- npm: `@backstage/core-components` — affected >=0 <0.12.4
- npm: `@backstage/catalog-model` — affected >=0 <1.2.0
- npm: `@backstage/plugin-catalog-backend` — affected >=0 <1.7.2

## Details
### Impact

This vulnerability allows a malicious actor with access to add or modify content in an instance of the Backstage software catalog to inject script URLs in the entities stored in the catalog. If users of the catalog then click on said URLs, that can lead to an XSS attack.

### Patches

This vulnerability has been patched in both the frontend and backend implementations. The default `Link` component from `@backstage/core-components` will now reject `javascript:` URLs, and there is a global override of `window.open` to do the same.

In addition the catalog model as well as the catalog backend now has additional validation built in that prevents `javascript:` URLs in known annotations.

### Workarounds

The general practice of limiting access to modifying catalog content and requiring code reviews greatly helps mitigate this vulnerability.

### For more information

If you have any questions or comments about this advisory:

* Open an issue in the [Backstage repository](https://github.com/backstage/backstage)
* Visit our chat, linked to in the [Backstage README](https://github.com/backstage/backstage)

## References
- https://github.com/backstage/backstage/security/advisories/GHSA-7hv8-3fr9-j2hv
- https://nvd.nist.gov/vuln/detail/CVE-2023-25571
- https://github.com/backstage/backstage/commit/3d1371954512f7fa8bd0e2d357e00eada2c3e8a8
- https://github.com/backstage/backstage
