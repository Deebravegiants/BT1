# [C] Deserialization of Untrusted Data in superset

## Summary
Severity: Critical
Advisory: GHSA-vxp9-wv2f-wqmw
CVE: CVE-2018-8021
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-11-09
Source: https://github.com/advisories/GHSA-vxp9-wv2f-wqmw
Type: github-advisory

## Affected
- PyPI: `superset` — affected >=0 <0.23

## Details
Versions of Superset prior to 0.23 used an unsafe load method from the pickle library to deserialize data leading to possible remote code execution. Note Superset 0.23 was released prior to any Superset release under the Apache Software Foundation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8021
- https://github.com/apache/incubator-superset/pull/4243
- https://github.com/apache/superset/pull/4243
- https://github.com/apache/superset/commit/2c72a7ae4fc0a8bac1f037a79efa90e1c5549710
- https://github.com/advisories/GHSA-vxp9-wv2f-wqmw
- https://github.com/apache/superset
- https://github.com/pypa/advisory-database/tree/main/vulns/superset/PYSEC-2018-74.yaml
- https://www.exploit-db.com/exploits/45933
