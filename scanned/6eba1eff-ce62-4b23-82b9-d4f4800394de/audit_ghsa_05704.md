# [H] Langflow affected by Remote Code Execution via validate_code() exec()

## Summary
Severity: High
Advisory: GHSA-g22f-v6f7-2hrh
CVE: CVE-2026-0770
CWE: CWE-829
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-01-23
Source: https://github.com/advisories/GHSA-g22f-v6f7-2hrh
Type: github-advisory

## Affected
- PyPI: `langflow` — affected >=0

## Details
Langflow exec_globals Inclusion of Functionality from Untrusted Control Sphere Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of Langflow. Authentication is not required to exploit this vulnerability.

The specific flaw exists within the handling of the exec_globals parameter provided to the validate endpoint. The issue results from the inclusion of a resource from an untrusted control sphere. An attacker can leverage this vulnerability to execute code in the context of root. Was ZDI-CAN-27325.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-0770
- https://github.com/affix/CVE-2026-0770-PoC
- https://github.com/langflow-ai/langflow
- https://www.zerodayinitiative.com/advisories/ZDI-26-036
