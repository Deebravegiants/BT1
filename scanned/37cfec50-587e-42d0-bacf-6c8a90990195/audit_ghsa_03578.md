# [H] OMERO.web exposes some unnecessary session information in the page

## Summary
Severity: High
Advisory: GHSA-gfp2-w5jm-955q
CVE: CVE-2021-21376
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-03-23
Source: https://github.com/advisories/GHSA-gfp2-w5jm-955q
Type: github-advisory

## Affected
- PyPI: `omero-web` — affected >=0 <5.9.0

## Details
### Background
OMERO.web loads various information about the current user such as their id, name and the groups they are in, and these are available on the main webclient pages. Some additional information being loaded is not used by the webclient and is being removed in this release.

### Impact
OMERO.web before 5.9.0

### Patches
5.9.0

### Workarounds
No workaround

### References

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [omero-web](https://github.com/ome/omero-web)
* Email us at [security](mailto:security@openmicroscopy.org.uk)

## References
- https://github.com/ome/omero-web/security/advisories/GHSA-gfp2-w5jm-955q
- https://nvd.nist.gov/vuln/detail/CVE-2021-21376
- https://github.com/ome/omero-web/commit/952f8e5d28532fbb14fb665982211329d137908c
- https://github.com/ome/omero-web
- https://github.com/ome/omero-web/blob/master/CHANGELOG.md#590-march-2021
- https://github.com/pypa/advisory-database/tree/main/vulns/omero-web/PYSEC-2021-31.yaml
- https://pypi.org/project/omero-web
- https://www.openmicroscopy.org/security/advisories/2021-SV1
