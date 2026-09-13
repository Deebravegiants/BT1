# [C] Out-of-bounds read in Pillow

## Summary
Severity: Critical
Advisory: GHSA-43fq-w8qq-v88h
CVE: CVE-2020-11538
CWE: CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-07-27
Source: https://github.com/advisories/GHSA-43fq-w8qq-v88h
Type: github-advisory

## Affected
- PyPI: `pillow` — affected >=0 <7.1.0

## Details
In libImaging/SgiRleDecode.c in Pillow through 7.0.0, a number of out-of-bounds reads exist in the parsing of SGI image files, a different issue than CVE-2020-5311.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-11538
- https://github.com/python-pillow/Pillow/pull/4504
- https://github.com/python-pillow/Pillow/pull/4538
- https://github.com/python-pillow/Pillow/commit/2ef59fdbaeb756bc512ab3f2ad15ac45665b303d
- https://github.com/advisories/GHSA-43fq-w8qq-v88h
- https://github.com/pypa/advisory-database/tree/main/vulns/pillow/PYSEC-2020-80.yaml
- https://github.com/python-pillow/Pillow
- https://github.com/python-pillow/Pillow/blob/master/docs/releasenotes/7.1.0.rst#security
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/BEBCPE4F2VHTIT6EZA2YZQZLPVDEBJGD
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HOKHNWV2VS5GESY7IBD237E7C6T3I427
- https://pillow.readthedocs.io/en/stable/releasenotes/7.1.0.html
- https://pillow.readthedocs.io/en/stable/releasenotes/index.html
- https://snyk.io/vuln/SNYK-PYTHON-PILLOW-574574
- https://usn.ubuntu.com/4430-1
- https://usn.ubuntu.com/4430-2
