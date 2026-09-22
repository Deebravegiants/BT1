# [M] NFStream Local Denial of Service (DoS)

## Summary
Severity: Medium
Advisory: GHSA-whmq-cfm5-j8mj
CVE: CVE-2020-25340
CWE: CWE-401, CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-whmq-cfm5-j8mj
Type: github-advisory

## Affected
- PyPI: `nfstream` — affected 5.2.0

## Details
An issue was discovered in NFStream 5.2.0. Because some allocated modules are not correctly freed, if the nfstream object is directly destroyed without being used after it is created, it will cause a memory leak that may result in a local denial of service (DoS).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-25340
- https://github.com/ntop/nDPI/issues/994
- https://github.com/nfstream/nfstream
- https://github.com/pypa/advisory-database/tree/main/vulns/nfstream/PYSEC-2021-68.yaml
