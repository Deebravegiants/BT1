# [H] LoLLMS Path Traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-p8h7-c8gw-6x8c
CVE: CVE-2024-4881
CWE: CWE-22, CWE-36
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-06-06
Source: https://github.com/advisories/GHSA-p8h7-c8gw-6x8c
Type: github-advisory

## Affected
- PyPI: `lollms` — affected >=0 <9.5.0

## Details
A path traversal vulnerability exists in the parisneo/lollms application, affecting version 9.4.0 and potentially earlier versions, but fixed in version 9.5.0. The vulnerability arises due to improper validation of file paths between Windows and Linux environments, allowing attackers to traverse beyond the intended directory and read any file on the Windows system. Specifically, the application fails to adequately sanitize file paths containing backslashes (`\`), which can be exploited to access the root directory and read, or even delete, sensitive files. This issue was discovered in the context of the `/user_infos` endpoint, where a crafted request using backslashes to reference a file (e.g., `\windows\win.ini`) could result in unauthorized file access. The impact of this vulnerability includes the potential for attackers to access sensitive information such as environment variables, database files, and configuration files, which could lead to further compromise of the system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-4881
- https://github.com/parisneo/lollms/commit/95ad36eeffc6a6be3e3f35ed35a384d768f0ecf6
- https://github.com/parisneo/lollms
- https://huntr.com/bounties/94f7f901-80b0-4cf5-b545-ac5c1e7635e9
