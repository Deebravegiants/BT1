# [M] Open Chinese Convert subject to Denial of Service via Out-of-bounds Read

## Summary
Severity: Medium
Advisory: GHSA-9qh2-6fxg-9m4g
CVE: CVE-2018-16982
CWE: CWE-125
Ecosystem: npm
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-9qh2-6fxg-9m4g
Type: github-advisory

## Affected
- npm: `opencc` — affected >=0 <1.1.2

## Details
Open Chinese Convert (OpenCC) 1.0.5 allows attackers to cause a denial of service (segmentation fault) because BinaryDict::NewFromFile in BinaryDict.cpp may have out-of-bounds keyOffset and valueOffset values via a crafted .ocd file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16982
- https://github.com/BYVoid/OpenCC/issues/303
- https://github.com/BYVoid/OpenCC/pull/309
- https://github.com/BYVoid/OpenCC/pull/560
- https://github.com/BYVoid/OpenCC/pull/560/commits/e1b8c7949738100e4747dd4109ef1f16e1bd99c4
- https://github.com/BYVoid/OpenCC/commit/4a4f9e58e505fca93605f22363c133df66a91a5e
- https://github.com/BYVoid/OpenCC
- https://github.com/pypa/advisory-database/tree/main/vulns/opencc-py/PYSEC-2018-153.yaml
