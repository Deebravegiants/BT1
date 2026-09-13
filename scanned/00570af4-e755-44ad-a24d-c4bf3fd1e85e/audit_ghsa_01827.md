# [H] bounter Null pointer reference

## Summary
Severity: High
Advisory: GHSA-74xw-gwfm-7pv7
CVE: CVE-2021-41497
CWE: CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-12-18
Source: https://github.com/advisories/GHSA-74xw-gwfm-7pv7
Type: github-advisory

## Affected
- PyPI: `bounter` — affected >=0

## Details
Null pointer reference in CMS_Conservative_increment_obj in RaRe-Technologies bounter version 1.01 and 1.10, allows attackers to conduct Denial of Service attacks by inputting a huge width of hash bucket.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-41497
- https://github.com/RaRe-Technologies/bounter/issues/47
- https://github.com/RaRe-Technologies/bounter
- https://github.com/pypa/advisory-database/tree/main/vulns/bounter/PYSEC-2021-880.yaml
