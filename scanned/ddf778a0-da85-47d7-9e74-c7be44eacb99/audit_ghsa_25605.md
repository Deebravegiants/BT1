# [M] Multiple cross-site scripting (XSS) vulnerabilities in Roundup

## Summary
Severity: Medium
Advisory: GHSA-5jq3-8437-x35p
CVE: CVE-2012-6133
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-04-23
Source: https://github.com/advisories/GHSA-5jq3-8437-x35p
Type: github-advisory

## Affected
- PyPI: `roundup` — affected >=0 <1.4.20

## Details
Multiple cross-site scripting (XSS) vulnerabilities in Roundup before 1.4.20 allow remote attackers to inject arbitrary web script or HTML via the (1) @ok_message or (2) @error_message parameter to issue*.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-6133
- https://bugzilla.redhat.com/show_bug.cgi?id=722672
- https://github.com/advisories/GHSA-5jq3-8437-x35p
- https://github.com/pypa/advisory-database/tree/main/vulns/roundup/PYSEC-2020-212.yaml
- https://pypi.python.org/pypi/roundup/1.4.20
- http://hg.code.sf.net/p/roundup/code
- http://issues.roundup-tracker.org/issue2550724
- http://www.openwall.com/lists/oss-security/2012/11/10/2
- http://www.openwall.com/lists/oss-security/2013/02/13/8
