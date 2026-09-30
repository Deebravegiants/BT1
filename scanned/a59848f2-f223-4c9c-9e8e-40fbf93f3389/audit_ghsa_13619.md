# [C] SaToken privilege escalation vulnerability

## Summary
Severity: Critical
Advisory: GHSA-54f6-9mx9-86f7
CVE: CVE-2023-44794
CWE: CWE-281, CWE-284
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-10-25
Source: https://github.com/advisories/GHSA-54f6-9mx9-86f7
Type: github-advisory

## Affected
- Maven: `cn.dev33:sa-token-core` — affected >=0 <1.37.0

## Details
An issue in Dromara SaToken version 1.36.0 and before allows a remote attacker to escalate privileges via a crafted payload to the URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-44794
- https://github.com/dromara/Sa-Token/issues/515
- https://github.com/dromara/Sa-Token/commit/954efeb73277f924f836da2a25322ea35ee1bfa3
- https://github.com/dromara/Sa-Token
