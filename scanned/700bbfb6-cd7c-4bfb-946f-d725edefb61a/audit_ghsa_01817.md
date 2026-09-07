# [H] APM Java Agent Local Privilege Escalation

## Summary
Severity: High
Advisory: GHSA-r562-m862-63w3
CVE: CVE-2021-37941
CWE: CWE-269
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-12-09
Source: https://github.com/advisories/GHSA-r562-m862-63w3
Type: github-advisory

## Affected
- PyPI: `elastic-apm` — affected >=1.10.0 <1.27.0

## Details
A local privilege escalation issue was found with the APM Java agent, where a user on the system could attach a malicious file to an application running with the APM Java agent. Using this vector, a malicious or compromised user account could use the agent to run commands at a higher level of permissions than they possess. This vulnerability affects users that have set up the agent via the attacher cli 3, the attach API 2, as well as users that have enabled the profiling_inferred_spans_enabled option

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-37941
- https://discuss.elastic.co/t/apm-java-agent-security-update/289627
- https://github.com/elastic/apm-agent-python
