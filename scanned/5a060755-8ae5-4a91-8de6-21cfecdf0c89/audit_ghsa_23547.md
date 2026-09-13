# [C] AsyncSSH SSH Server Authentication Bypass

## Summary
Severity: Critical
Advisory: GHSA-97cv-6pjf-5f9q
CVE: CVE-2018-7749
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-97cv-6pjf-5f9q
Type: github-advisory

## Affected
- PyPI: `AsyncSSH` — affected >=0 <1.12.1

## Details
The SSH server implementation of AsyncSSH before 1.12.1 does not properly check whether authentication is completed before processing other requests. A customized SSH client can simply skip the authentication step.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-7749
- https://github.com/ronf/asyncssh/commit/16e6ebfa893167c7d9d3f6dc7a2c0d197e47f43a
- https://github.com/ronf/asyncssh/commit/c161e26cdc0d41b745b63d9f17b437f073bf7ba4
- https://github.com/pypa/advisory-database/tree/main/vulns/asyncssh/PYSEC-2018-108.yaml
- https://github.com/ronf/asyncssh
- https://groups.google.com/forum/#!msg/asyncssh-announce/57_5O7kiHSA/8BXZ_hxHAQAJ
