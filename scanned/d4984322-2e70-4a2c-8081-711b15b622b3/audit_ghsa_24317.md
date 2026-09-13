# [H] Aubio is vulnerable to denial of service via aubio_pitch_set_unit function

## Summary
Severity: High
Advisory: GHSA-g7g8-mx45-x4c8
CVE: CVE-2018-14522
CWE: CWE-119
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-g7g8-mx45-x4c8
Type: github-advisory

## Affected
- PyPI: `aubio` — affected >=0 <0.4.7

## Details
An issue was discovered in aubio 0.4.6. A SEGV signal can occur in `aubio_pitch_set_unit` in `pitch/pitch.c`, as demonstrated by aubionotes.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-14522
- https://github.com/aubio/aubio/issues/188
- https://github.com/aubio/aubio/commit/99c7aa2e3efec988a5f81018b48d9388ff24bba1
- https://github.com/aubio/aubio
- https://github.com/pypa/advisory-database/tree/main/vulns/aubio/PYSEC-2018-62.yaml
- http://lists.opensuse.org/opensuse-security-announce/2019-03/msg00031.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00071.html
