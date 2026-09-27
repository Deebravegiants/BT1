# [M] Tahoe-LAFS fails to ensure integrity

## Summary
Severity: Medium
Advisory: GHSA-v62p-cjv8-35xh
CVE: CVE-2012-0051
Ecosystem: PyPI
Published: 2022-04-23
Source: https://github.com/advisories/GHSA-v62p-cjv8-35xh
Type: github-advisory

## Affected
- PyPI: `tahoe-lafs` — affected 1.9.0

## Details
Tahoe-LAFS 1.9.0 fails to ensure integrity which allows remote attackers to corrupt mutable files or directories upon retrieval.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-0051
- https://github.com/pypa/advisory-database/tree/main/vulns/tahoe-lafs/PYSEC-2019-253.yaml
- https://github.com/tahoe-lafs/tahoe-lafs
- https://security-tracker.debian.org/tracker/CVE-2012-0051
- https://tahoe-lafs.org/trac/tahoe-lafs/ticket/1654
- http://www.openwall.com/lists/oss-security/2012/01/15/11
- http://www.openwall.com/lists/oss-security/2012/01/26/7
- http://www.openwall.com/lists/oss-security/2012/01/26/8
- http://www.openwall.com/lists/oss-security/2012/01/26/9
