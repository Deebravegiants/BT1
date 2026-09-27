# [H] Numpy arbitrary file write via symlink attack

## Summary
Severity: High
Advisory: GHSA-2fc2-6r4j-p65h
CVE: CVE-2014-1859
CWE: CWE-59
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-2fc2-6r4j-p65h
Type: github-advisory

## Affected
- PyPI: `numpy` — affected >=0 <1.8.1

## Details
(1) core/tests/test_memmap.py, (2) core/tests/test_multiarray.py, (3) f2py/f2py2e.py, and (4) lib/tests/test_io.py in NumPy before 1.8.1 allow local users to write to arbitrary files via a symlink attack on a temporary file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-1859
- https://github.com/numpy/numpy/pull/4262
- https://github.com/numpy/numpy/commit/0bb46c1448b0d3f5453d5182a17ea7ac5854ee15
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=737778
- https://bugzilla.redhat.com/show_bug.cgi?id=1062009
- https://exchange.xforce.ibmcloud.com/vulnerabilities/91317
- https://github.com/advisories/GHSA-2fc2-6r4j-p65h
- https://github.com/numpy/numpy
- https://github.com/numpy/numpy/blob/maintenance/1.8.x/doc/release/1.8.1-notes.rst
- https://github.com/pypa/advisory-database/tree/main/vulns/numpy/PYSEC-2018-34.yaml
- https://web.archive.org/web/20200228165750/http://www.securityfocus.com/bid/65440
- http://lists.fedoraproject.org/pipermail/package-announce/2014-February/128358.html
- http://lists.fedoraproject.org/pipermail/package-announce/2014-February/128781.html
- http://www.openwall.com/lists/oss-security/2014/02/08/3
