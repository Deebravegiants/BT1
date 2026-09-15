# [C] Scalyr Agent Missing SSL Certificate Validation

## Summary
Severity: Critical
Advisory: GHSA-w6xv-mf6f-r5f6
CVE: CVE-2020-24714
CWE: CWE-295
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-w6xv-mf6f-r5f6
Type: github-advisory

## Affected
- PyPI: `scalyr-agent-2` — affected >=0 <2.1.10

## Details
The Scalyr Agent before 2.1.10 has Missing SSL Certificate Validation because, in some circumstances, the openssl binary is called without the -verify_hostname option.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-24714
- https://github.com/scalyr/scalyr-agent-2/commit/96d5f5bec734c7a0e7c64654cdb7aacc81fdc867
- https://github.com/pypa/advisory-database/tree/main/vulns/scalyr-agent-2/PYSEC-2020-251.yaml
- https://github.com/scalyr/scalyr-agent-2
- https://github.com/scalyr/scalyr-agent-2/blob/96d5f5bec734c7a0e7c64654cdb7aacc81fdc867/CHANGELOG.md
- https://scalyr-static.s3.amazonaws.com/technical-details/index.html
