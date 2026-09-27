# [M] OMERO-web Sensitive Data Exposure

## Summary
Severity: Medium
Advisory: GHSA-vwxv-frj6-fhc9
CVE: CVE-2020-7932
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-vwxv-frj6-fhc9
Type: github-advisory

## Affected
- PyPI: `omero-web` — affected >=0 <5.6.3

## Details
OMERO.web before 5.6.3 optionally allows sensitive data elements (e.g., a session key) to be passed as URL query parameters. If an attacker tricks a user into clicking a malicious link in OMERO.web, the information in the query parameters may be exposed in the Referer header seen by the target. Information in the URL path such as object IDs may also be exposed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7932
- https://github.com/ome/omero-web
- https://github.com/pypa/advisory-database/tree/main/vulns/omero-web/PYSEC-2020-244.yaml
- https://www.openmicroscopy.org/security/advisories/2019-SV4
