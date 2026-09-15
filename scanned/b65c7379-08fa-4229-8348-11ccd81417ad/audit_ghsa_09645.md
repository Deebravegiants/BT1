# [H] pygeoapi 0.23.x: Path Traversal in STAC FileSystemProvider

## Summary
Severity: High
Advisory: GHSA-f6pr-83pg-ghh6
CVE: CVE-2026-42351
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-f6pr-83pg-ghh6
Type: github-advisory

## Affected
- PyPI: `pygeoapi` — affected >=0.23.0 <0.23.3

## Details
### Impact
A raw string path concatenation vulnerability in pygeoapi's STAC FileSystemProvider plugin can allow for requests to STAC collection based collections to expose directories without authentication.  The issue manifests when pygeoapi is deployed without a proxy or web front end that would normalize URLs with `..` values, along with a resource of type `stac-collection` defined in configuration.

### Patches
The issue has been patched in master branch and made available as part of the 0.23.3 release.

The commit/fix can be found in [bf25b8695edbdd5476eeffc102b633d1d3e45f52](https://github.com/geopython/pygeoapi/commit/bf25b8695edbdd5476eeffc102b633d1d3e45f52).
### Workarounds
Users can safeguard existing applications by disabling STAC collection based resources in their pygeoapi config, until 0.23.3 can be installed and deployed.

## References
- https://github.com/geopython/pygeoapi/security/advisories/GHSA-f6pr-83pg-ghh6
- https://nvd.nist.gov/vuln/detail/CVE-2026-42351
- https://github.com/geopython/pygeoapi/commit/bf25b8695edbdd5476eeffc102b633d1d3e45f52
- https://github.com/geopython/pygeoapi
- https://github.com/geopython/pygeoapi/releases/tag/0.23.3
