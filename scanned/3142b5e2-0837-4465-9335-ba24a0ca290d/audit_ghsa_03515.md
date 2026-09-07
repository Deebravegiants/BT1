# [M] OMERO webclient does not validate URL redirects on login or switching group.

## Summary
Severity: Medium
Advisory: GHSA-g4rf-pc26-6hmr
CVE: CVE-2021-21377
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-03-23
Source: https://github.com/advisories/GHSA-g4rf-pc26-6hmr
Type: github-advisory

## Affected
- PyPI: `omero-web` — affected >=0 <5.9.0

## Details
### Background
OMERO.web supports redirection to a given URL after performing login or switching the group context. These URLs are not validated, allowing redirection to untrusted sites. OMERO.web 5.9.0 adds URL validation before redirecting. External URLs are not considered valid, unless specified in the ``omero.web.redirect_allowed_hosts`` setting.

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
- https://github.com/ome/omero-web/security/advisories/GHSA-g4rf-pc26-6hmr
- https://nvd.nist.gov/vuln/detail/CVE-2021-21377
- https://github.com/ome/omero-web/commit/952f8e5d28532fbb14fb665982211329d137908c
- https://github.com/ome/omero-web
- https://github.com/ome/omero-web/blob/master/CHANGELOG.md#590-march-2021
- https://github.com/pypa/advisory-database/tree/main/vulns/omero-web/PYSEC-2021-32.yaml
- https://pypi.org/project/omero-web
- https://www.openmicroscopy.org/security/advisories/2021-SV2
