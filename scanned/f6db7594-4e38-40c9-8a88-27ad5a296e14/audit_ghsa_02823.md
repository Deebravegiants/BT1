# [C] Inconsistent input sanitisation leads to XSS vectors

## Summary
Severity: Critical
Advisory: GHSA-g67g-hvc3-xmvf
CVE: CVE-2021-41132
CWE: CWE-116, CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-10-14
Source: https://github.com/advisories/GHSA-g67g-hvc3-xmvf
Type: github-advisory

## Affected
- PyPI: `omero-web` — affected >=0 <5.11.0
- PyPI: `omero-figure` — affected >=0 <4.4.1

## Details
### Background

A variety of templates do not perform proper sanitization through HTML escaping.
Due to the lack of sanitization and use of ``jQuery.html()``, there are a whole host of XSS possibilities with specially crafted input to a variety of fields.

### Impact

OMERO.web before 5.11.0 and OMERO.figure before 4.4.1.

### Patches
Users should upgrade OMERO.web to 5.11.0 or higher and OMERO.figure to 4.4.1 or higher.

## References
- https://github.com/ome/omero-web/security/advisories/GHSA-g67g-hvc3-xmvf
- https://nvd.nist.gov/vuln/detail/CVE-2021-41132
- https://github.com/ome/omero-web/commit/0168067accde5e635341b3c714b1d53ae92ba424
- https://github.com/ome/omero-web
- https://github.com/pypa/advisory-database/tree/main/vulns/omero-figure/PYSEC-2021-379.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/omero-web/PYSEC-2021-372.yaml
- https://www.openmicroscopy.org/security/advisories/2021-SV3
