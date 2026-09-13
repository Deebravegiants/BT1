# [M] Elastic APM agent for Python client CGI proxy redirection flaw

## Summary
Severity: Medium
Advisory: GHSA-22jh-6gx8-f944
CVE: CVE-2019-7617
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-22jh-6gx8-f944
Type: github-advisory

## Affected
- PyPI: `elastic-apm` — affected >=0 <5.1.0

## Details
When the Elastic APM agent for Python versions before 5.1.0 is run as a CGI script, there is a variable name clash flaw if a remote attacker can control the proxy header. This could result in an attacker redirecting collected APM data to a proxy of their choosing.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-7617
- https://discuss.elastic.co/t/elastic-apm-agent-for-python-5-1-0-security-update/196145
- https://github.com/elastic/apm-agent-python
- https://github.com/pypa/advisory-database/tree/main/vulns/elastic-apm/PYSEC-2019-178.yaml
- https://www.elastic.co/community/security
