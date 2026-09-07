# [C] Command injection in LocalStack

## Summary
Severity: Critical
Advisory: GHSA-hpr6-f4vq-mxch
CVE: CVE-2021-32090
CWE: CWE-77
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-06-18
Source: https://github.com/advisories/GHSA-hpr6-f4vq-mxch
Type: github-advisory

## Affected
- PyPI: `localstack` — affected >=0 <0.12.10

## Details
The dashboard component of StackLift LocalStack allows attackers to inject arbitrary shell commands via the functionName parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-32090
- https://github.com/localstack/localstack/commit/01cd169ae5d077693d4c1a4679a95e30b8d44d54
- https://blog.sonarsource.com/hack-the-stack-with-localstack
- https://github.com/advisories/GHSA-hpr6-f4vq-mxch
- https://github.com/localstack/localstack
- https://github.com/pypa/advisory-database/tree/main/vulns/localstack/PYSEC-2021-101.yaml
- https://portswigger.net/daily-swig/localstack-zero-day-vulnerabilities-chained-to-achieve-remote-takeover-of-local-instances
