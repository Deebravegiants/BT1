# [H] rdiffweb's lack of token name length limit can result in DoS or memory corruption

## Summary
Severity: High
Advisory: GHSA-3fhq-72hw-jqwv
CVE: CVE-2022-3371
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-10-01
Source: https://github.com/advisories/GHSA-3fhq-72hw-jqwv
Type: github-advisory

## Affected
- PyPI: `rdiffweb` — affected >=0 <2.5.0a3

## Details
rdiffweb prior to 2.5.0a3 is vulnerable to Allocation of Resources Without Limits or Throttling. A lack of limit in the length of the `Token name` parameter can result in denial of service or memory corruption. Version 2.5.0a3 fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3371
- https://github.com/ikus060/rdiffweb/commit/b62c479ff6979563c7c23e7182942bc4f460a2c7
- https://github.com/ikus060/rdiffweb
- https://github.com/pypa/advisory-database/tree/main/vulns/rdiffweb/PYSEC-2022-299.yaml
- https://huntr.dev/bounties/4e8f6136-50c7-4fa1-ac98-699bcb7b35ce
