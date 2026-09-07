# [H] tlslite remote denial of service vulnerability

## Summary
Severity: High
Advisory: GHSA-4749-p7rx-8jjj
CVE: CVE-2015-3220
CWE: CWE-119
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-4749-p7rx-8jjj
Type: github-advisory

## Affected
- PyPI: `tlslite` — affected >=0 <0.4.9

## Details
The tlslite library before 0.4.9 for Python allows remote attackers to trigger a denial of service (runtime exception and process crash).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-3220
- https://github.com/trevp/tlslite/commit/aca8d4f898b436ff6754e1a9ab96cae976c8a853
- https://bugzilla.redhat.com/show_bug.cgi?id=1254215
- https://github.com/pypa/advisory-database/tree/main/vulns/tlslite/PYSEC-2017-96.yaml
- https://github.com/trevp/tlslite
- https://groups.google.com/forum/#!topic/tlslite-dev/MoWE7B0A4iU
