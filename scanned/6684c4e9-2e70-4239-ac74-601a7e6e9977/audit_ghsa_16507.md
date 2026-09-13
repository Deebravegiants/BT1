# [M] OMERO.web must check that the JSONP callback is a valid function

## Summary
Severity: Medium
Advisory: GHSA-vr85-5pwx-c6gq
CVE: CVE-2024-35180
CWE: CWE-830
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-21
Source: https://github.com/advisories/GHSA-vr85-5pwx-c6gq
Type: github-advisory

## Affected
- PyPI: `omero-web` — affected >=0 <5.26.0

## Details
### Background

There is currently no escaping or validation of the `callback` parameter that can be passed to various OMERO.web endpoints that have JSONP enabled. One such endpoint is `/webclient/imgData/...`. As we only really use these endpoints with jQuery's own callback name generation [^1] it is quite difficult or even impossible to exploit this in vanilla OMERO.web. However, these metadata endpoints are likely to be used by many plugins.

[^1]: https://learn.jquery.com/ajax/working-with-jsonp/

### Impact
OMERO.web before 5.25.0

### Patches
Users should upgrade to 5.26.0 or higher
### Workarounds

None

### References
* https://stackoverflow.com/questions/2777021/do-i-need-to-sanitize-the-callback-parameter-from-a-jsonp-call
* https://stackoverflow.com/questions/1661197/what-characters-are-valid-for-javascript-variable-names

For more information
If you have any questions or comments about this advisory:

Open an issue in [omero-web](https://github.com/ome/omero-web)
Email us at [security@openmicroscopy.org](mailto:security@openmicroscopy.org)

## References
- https://github.com/ome/omero-web/security/advisories/GHSA-vr85-5pwx-c6gq
- https://nvd.nist.gov/vuln/detail/CVE-2024-35180
- https://github.com/ome/omero-web/commit/d41207cbb82afc56ea79e84db532608aa24ab4aa
- https://github.com/ome/omero-web
