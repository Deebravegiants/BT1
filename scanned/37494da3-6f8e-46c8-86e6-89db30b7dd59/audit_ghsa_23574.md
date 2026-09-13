# [H] RhodeCode and Kallithea are vulnerable to sensitive information disclosure

## Summary
Severity: High
Advisory: GHSA-hhx9-4vw2-x54r
CVE: CVE-2015-0260
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-hhx9-4vw2-x54r
Type: github-advisory

## Affected
- PyPI: `RhodeCode` — affected >=0 <2.2.7
- PyPI: `Kallithea` — affected >=0 <0.2

## Details
RhodeCode before 2.2.7 and Kallithea 0.1 allows remote authenticated users to obtain API keys and other sensitive information via the get_repo API method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-0260
- https://exchange.xforce.ibmcloud.com/vulnerabilities/100888
- https://github.com/pypa/advisory-database/tree/main/vulns/kallithea/PYSEC-2015-29.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/rhodecode/PYSEC-2015-32.yaml
- https://kallithea-scm.org/repos/kallithea/changeset/5923d74742879b812965568475e21c3496d722a9
- https://kallithea-scm.org/security/cve-2015-0260.html
- https://rhodecode.com/blog/rhodecode-enterprise-security-release
- https://web.archive.org/web/20150321135511/http://www.securityfocus.com/bid/72573
- http://seclists.org/oss-sec/2015/q1/505
