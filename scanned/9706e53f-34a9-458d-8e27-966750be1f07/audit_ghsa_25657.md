# [H] Apache Doris hardcoded key and IV

## Summary
Severity: High
Advisory: GHSA-98j2-hfxp-8h8r
CVE: CVE-2022-23942
CWE: CWE-798
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-04-27
Source: https://github.com/advisories/GHSA-98j2-hfxp-8h8r
Type: github-advisory

## Affected
- PyPI: `pydoris` — affected >=0 <1.0.0

## Details
Apache Doris, prior to 1.0.0, used a hardcoded key and IV to initialize the cipher used for ldap password, which may lead to information disclosure.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-23942
- https://github.com/apache/doris
- https://github.com/pypa/advisory-database/tree/main/vulns/pydoris/PYSEC-2022-43150.yaml
- https://lists.apache.org/thread/com2dyzp3bn2rdrotry90q2zzord4tvt
- http://www.openwall.com/lists/oss-security/2022/04/26/2
- http://www.openwall.com/lists/oss-security/2022/04/26/3
