# [H] XWiki allows remote code execution through preview of XClass changes in AWM editor

## Summary
Severity: High
Advisory: GHSA-jp4x-w9cj-97q7
CVE: CVE-2025-49586
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-06-13
Source: https://github.com/advisories/GHSA-jp4x-w9cj-97q7
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=7.2-milestone-2 <16.4.7
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=16.5.0-rc-1 <16.10.3
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=17.0.0-rc-1 <17.0.0

## Details
### Impact
Any XWiki user with edit right on at least one App Within Minutes application (the default for all users XWiki) can obtain programming right/perform remote code execution by editing the application. The detailed reproduction steps can be found in the [original bug report](https://jira.xwiki.org/browse/XWIKI-22719).

### Patches
This vulnerability has been fixed in XWiki 17.0.0, 16.4.7, and 16.10.3.

### Workarounds
Restricting edit rights on all existing App Within Minutes applications to trusted users mitigates at least the PoC exploit, but we can't exclude that there are other ways to exploit this vulnerability.

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-jp4x-w9cj-97q7
- https://nvd.nist.gov/vuln/detail/CVE-2025-49586
- https://github.com/xwiki/xwiki-platform/commit/ef978315649cf83eae396021bb33603a1a5f7e42
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-22719
