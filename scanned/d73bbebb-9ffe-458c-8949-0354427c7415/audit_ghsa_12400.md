# [M] Displayed in plain text by Dingding JSON Pusher Plugin 

## Summary
Severity: Medium
Advisory: GHSA-q5cj-xf99-79m8
CVE: CVE-2023-50773
CWE: CWE-200, CWE-312
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-12-13
Source: https://github.com/advisories/GHSA-q5cj-xf99-79m8
Type: github-advisory

## Affected
- Maven: `com.zintow:dingding-json-pusher` — affected >=0

## Details
Jenkins Dingding JSON Pusher Plugin 2.0 and earlier does not mask access tokens displayed on the job configuration form, increasing the potential for attackers to observe and capture them.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-50773
- https://www.jenkins.io/security/advisory/2023-12-13/#SECURITY-3184
- http://www.openwall.com/lists/oss-security/2023/12/13/4
