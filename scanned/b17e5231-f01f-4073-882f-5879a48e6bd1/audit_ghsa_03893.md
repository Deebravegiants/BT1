# [C] Uncontrolled deserialization of a pickled object in rediswrapper allows attackers to execute arbitrary scripts

## Summary
Severity: Critical
Advisory: GHSA-vrcf-g539-x6h3
CVE: CVE-2019-17206
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-11-20
Source: https://github.com/advisories/GHSA-vrcf-g539-x6h3
Type: github-advisory

## Affected
- PyPI: `rediswrapper` — affected >=0 <0.3.0

## Details
Uncontrolled deserialization of a pickled object in models.py in Frost Ming rediswrapper (aka Redis Wrapper) before 0.3.0 allows attackers to execute arbitrary scripts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-17206
- https://github.com/frostming/rediswrapper/pull/1
- https://github.com/frostming/rediswrapper/commit/748f60bafd857c24f65683426f665350e2c3f91b
- https://github.com/advisories/GHSA-vrcf-g539-x6h3
- https://github.com/frostming/rediswrapper
- https://github.com/frostming/rediswrapper/compare/v0.2.1...v0.3.0
- https://github.com/frostming/rediswrapper/releases/tag/v0.3.0
- https://github.com/pypa/advisory-database/tree/main/vulns/rediswrapper/PYSEC-2019-116.yaml
