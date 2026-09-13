# [M] Path traversal

## Summary
Severity: Medium
Advisory: GHSA-pgf8-28gg-vpr6
CVE: CVE-2021-32662
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-06-04
Source: https://github.com/advisories/GHSA-pgf8-28gg-vpr6
Type: github-advisory

## Affected
- npm: `@backstage/techdocs-common` — affected >=0 <0.6.3

## Details
### Impact

A malicious actor could read sensitive files from the environment where TechDocs documentation is built and published by setting a particular path for `docs_dir` in `mkdocs.yml`. These files would then be available over the TechDocs backend API.

This vulnerability is mitigated by the fact that an attacker would need access to modify the `mkdocs.yml` in the documentation source code, and would also need access to the TechDocs backend API.

### Patches

The vulnerability is patched in the `0.6.3` release of `@backstage/techdocs-common`.

### For more information

If you have any questions or comments about this advisory:

* Open an issue in the [Backstage repository](https://github.com/backstage/backstage)
* Visit our chat, linked to in [Backstage README](https://github.com/backstage/backstage)

## References
- https://github.com/backstage/backstage/security/advisories/GHSA-pgf8-28gg-vpr6
- https://nvd.nist.gov/vuln/detail/CVE-2021-32662
- https://github.com/backstage/backstage/commit/8cefadca04cbf01d0394b0cb1983247e5f1d6208
- https://github.com/backstage/backstage/releases/tag/release-2021-05-27
