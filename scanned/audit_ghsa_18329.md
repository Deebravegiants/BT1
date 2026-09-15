# [C] TkEasyGUI Vulnerable to OS Command Injection

## Summary
Severity: Critical
Advisory: GHSA-hfrj-3w3g-jv32
CVE: CVE-2025-55037
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-09-05
Source: https://github.com/advisories/GHSA-hfrj-3w3g-jv32
Type: github-advisory

## Affected
- PyPI: `TkEasyGUI` — affected >=0 <1.0.22

## Details
Improper neutralization of special elements used in an OS command ('OS Command Injection') issue exists in TkEasyGUI versions prior to v1.0.22. If this vulnerability is exploited, an arbitrary OS command may be executed by a remote unauthenticated attacker if the settings are configured to construct messages from external sources.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-55037
- https://github.com/kujirahand/tkeasygui-python
- https://github.com/kujirahand/tkeasygui-python/releases/tag/v1.0.22
- https://jvn.jp/en/jp/JVN48739895
