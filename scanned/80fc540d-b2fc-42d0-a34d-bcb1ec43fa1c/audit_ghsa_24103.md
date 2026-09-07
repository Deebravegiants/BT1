# [M] Cherry Music Cross-site Scripting (XSS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-4wcc-jv3p-prqw
CVE: CVE-2015-8310
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-4wcc-jv3p-prqw
Type: github-advisory

## Affected
- PyPI: `CherryMusic` — affected >=0 <0.36.0

## Details
Cross-site scripting (XSS) vulnerability in Cherry Music before 0.36.0 allows remote authenticated users to inject arbitrary web script or HTML via the playlistname field when creating a new playlist.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-8310
- https://github.com/devsnd/cherrymusic/issues/598
- https://github.com/devsnd/cherrymusic/commit/62dec34a1ea0741400dd6b6c660d303dcd651e86
- https://github.com/devsnd/cherrymusic
- https://github.com/pypa/advisory-database/tree/main/vulns/cherrymusic/PYSEC-2017-100.yaml
- https://web.archive.org/web/20200227183347/http://www.securityfocus.com/bid/97148
- http://www.fomori.org/cherrymusic/Changes.html
