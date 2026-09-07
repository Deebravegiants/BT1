# [H] Mailman Core vulnerable to timing attacks

## Summary
Severity: High
Advisory: GHSA-2jg5-xgvv-4wq7
CVE: CVE-2021-34337
CWE: CWE-208
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-04-15
Source: https://github.com/advisories/GHSA-2jg5-xgvv-4wq7
Type: github-advisory

## Affected
- PyPI: `mailman` — affected >=0 <3.3.5

## Details
An issue was discovered in Mailman Core before 3.3.5. An attacker with access to the REST API could use timing attacks to determine the value of the configured REST API password and then make arbitrary REST API calls. The REST API is bound to localhost by default, limiting the ability for attackers to exploit this, but can optionally be made to listen on other interfaces.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-34337
- https://github.com/pypa/advisory-database/tree/main/vulns/mailman/PYSEC-2023-22.yaml
- https://gitlab.com/mailman/mailman
- https://gitlab.com/mailman/mailman/-/commit/e4a39488c4510fcad8851217f10e7337a196bb51
- https://gitlab.com/mailman/mailman/-/issues/911
- https://gitlab.com/mailman/mailman/-/tags
