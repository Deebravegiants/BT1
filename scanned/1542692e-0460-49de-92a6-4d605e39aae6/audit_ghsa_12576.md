# [C] Dynamic Linq vulnerable to remote code execution

## Summary
Severity: Critical
Advisory: GHSA-w65q-jcmv-28gj
CVE: CVE-2023-32571
CWE: CWE-697
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-06-22
Source: https://github.com/advisories/GHSA-w65q-jcmv-28gj
Type: github-advisory

## Affected
- NuGet: `System.Linq.Dynamic.Core` — affected >=1.0.7.10 <1.3.0

## Details
Dynamic Linq 1.0.7.10 through 1.2.25 before 1.3.0 allows attackers to execute arbitrary code and commands when untrusted input to methods including Where, Select, OrderBy is parsed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-32571
- https://github.com/zzzprojects/System.Linq.Dynamic.Core
- https://research.nccgroup.com/2023/06/13/dynamic-linq-injection-remote-code-execution-vulnerability-cve-2023-32571
