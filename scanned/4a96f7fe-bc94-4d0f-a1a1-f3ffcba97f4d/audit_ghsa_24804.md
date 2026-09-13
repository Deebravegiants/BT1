# [M] pip lack of randomness in build directory

## Summary
Severity: Medium
Advisory: GHSA-53mr-44pp-crf4
CVE: CVE-2014-8991
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-53mr-44pp-crf4
Type: github-advisory

## Affected
- PyPI: `pip` — affected >=1.3 <6.0

## Details
pip 1.3 through 1.5.6 allows local users to cause a denial of service (prevention of package installation) by creating a `/tmp/pip-build-*` file for another user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-8991
- https://github.com/pypa/pip/pull/2122
- https://github.com/pypa/pip/commit/043fe9f5700315d97f83609c1f59deece8f1b901
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=725847
- https://github.com/pypa/advisory-database/tree/main/vulns/pip/PYSEC-2014-11.yaml
- https://github.com/pypa/pip
- http://www.openwall.com/lists/oss-security/2014/11/19/17
- http://www.openwall.com/lists/oss-security/2014/11/20/6
- http://www.oracle.com/technetwork/topics/security/bulletinjul2015-2511963.html
