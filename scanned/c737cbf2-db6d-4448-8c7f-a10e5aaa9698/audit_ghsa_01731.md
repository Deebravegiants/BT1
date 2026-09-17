# [H] Uncontrolled Resource Consumption in Pillow

## Summary
Severity: High
Advisory: GHSA-5gm3-px64-rw72
CVE: CVE-2019-19911
CWE: CWE-190
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2020-04-01
Source: https://github.com/advisories/GHSA-5gm3-px64-rw72
Type: github-advisory

## Affected
- PyPI: `pillow` — affected >=0 <6.2.2

## Details
There is a DoS vulnerability in Pillow before 6.2.2 caused by FpxImagePlugin.py calling the range function on an unvalidated 32-bit integer if the number of bands is large. On Windows running 32-bit Python, this results in an OverflowError or MemoryError due to the 2 GB limit. However, on Linux running 64-bit Python this results in the process being terminated by the OOM killer.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-19911
- https://github.com/python-pillow/Pillow/commit/774e53bb132461d8d5ebefec1162e29ec0ebc63d
- https://github.com/advisories/GHSA-5gm3-px64-rw72
- https://github.com/pypa/advisory-database/tree/main/vulns/pillow/PYSEC-2020-172.yaml
- https://github.com/python-pillow/Pillow/blob/master/CHANGES.rst#622-2020-01-02
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/3DUMIBUYGJRAVJCTFUWBRLVQKOUTVX5P
- https://pillow.readthedocs.io/en/stable/releasenotes/6.2.2.html
- https://usn.ubuntu.com/4272-1
- https://www.debian.org/security/2020/dsa-4631
