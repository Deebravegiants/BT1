# [H] pygeoapi 0.23.x: Unauthenticated SSRF via OGC API - Processes Subscriber  

## Summary
Severity: High
Advisory: GHSA-jgvc-94c8-3chc
CVE: CVE-2026-42352
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-jgvc-94c8-3chc
Type: github-advisory

## Affected
- PyPI: `pygeoapi` — affected >=0.23.0 <0.23.3

## Details
### Impact
OGC API - Process execution requests can use the `subscriber` object to requests to internal HTTP services.

### Patches
The issue has been patched in master branch and made available as part of the 0.23.3 release.  The patch disables any HTTP requests made to internal resources by default (unless explicitly defined in configuration by a new `allow_internal_requests` directive.

The commit/fix can be found in [3a63f5b0cc6275e3ae0edb47726b13a43cdd90ef](https://github.com/geopython/pygeoapi/commit/3a63f5b0cc6275e3ae0edb47726b13a43cdd90ef).

### Workarounds
Users can update existing applications by disabling process based resources in their pygeoapi config, until 0.23.3 can be installed and deployed.

## References
- https://github.com/geopython/pygeoapi/security/advisories/GHSA-jgvc-94c8-3chc
- https://nvd.nist.gov/vuln/detail/CVE-2026-42352
- https://github.com/geopython/pygeoapi/commit/3a63f5b0cc6275e3ae0edb47726b13a43cdd90ef
- https://github.com/geopython/pygeoapi
- https://github.com/geopython/pygeoapi/releases/tag/0.23.3
