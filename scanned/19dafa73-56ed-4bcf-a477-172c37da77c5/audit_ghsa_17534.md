# [H] XWiki's required right warnings for macros are incomplete

## Summary
Severity: High
Advisory: GHSA-c32m-27pj-4xcj
CVE: CVE-2025-49582
CWE: CWE-357
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-06-13
Source: https://github.com/advisories/GHSA-c32m-27pj-4xcj
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-rendering-xwiki` — affected >=15.9-rc-1 <16.4.7
- Maven: `org.xwiki.platform:xwiki-platform-rendering-xwiki` — affected >=16.5.0-rc-1 <16.10.3
- Maven: `org.xwiki.platform:xwiki-platform-rendering-xwiki` — affected >=17.0.0-rc-1 <17.0.0
- Maven: `org.xwiki.platform:xwiki-platform-rendering-macro-cache` — affected >=15.9-rc-1 <16.4.7
- Maven: `org.xwiki.platform:xwiki-platform-rendering-macro-cache` — affected >=16.5.0-rc-1 <16.10.3
- Maven: `org.xwiki.platform:xwiki-platform-rendering-macro-cache` — affected >=17.0.0-rc-1 <17.0.0
- Maven: `org.xwiki.platform:xwiki-platform-security-requiredrights-default` — affected >=15.9-rc-1 <16.4.7
- Maven: `org.xwiki.platform:xwiki-platform-security-requiredrights-default` — affected >=16.5.0-rc-1 <16.10.3
- Maven: `org.xwiki.platform:xwiki-platform-security-requiredrights-default` — affected >=17.0.0-rc-1 <17.0.0
- Maven: `org.xwiki.platform:xwiki-platform-rendering-macro-context` — affected >=15.9-rc-1 <16.4.7
- Maven: `org.xwiki.platform:xwiki-platform-rendering-macro-context` — affected >=16.5.0-rc-1 <16.10.3
- Maven: `org.xwiki.platform:xwiki-platform-rendering-macro-context` — affected >=17.0.0-rc-1 <17.0.0

## Details
### Impact
When editing content that contains "dangerous" macros like malicious script macros that were authored by a user with fewer rights, XWiki warns about the execution of these macros since XWiki 15.9RC1. These required rights analyzers that trigger these warnings are incomplete, allowing an attacker to hide malicious content. For most macros, the existing analyzers don't consider non-lowercase parameters. Further, most macro parameters that can contain XWiki syntax like titles of information boxes weren't analyzed at all. Similarly, the "source" parameters of the content and context macro weren't anylzed even though they could contain arbitrary XWiki syntax. In the worst case, this could allow a malicious to add malicious script macros including Groovy or Python macros to a page that are then executed after another user with programming righs edits the page, thus allowing remote code execution.

### Patches
The required rights analyzers have been made more robust and extended to cover those cases in XWiki 16.4.7, 16.10.3 and 17.0.0.

### Workarounds
We're not aware of any workarounds except for being careful when editing content authored by untrusted users.

### References
* https://jira.xwiki.org/browse/XWIKI-22763
* https://jira.xwiki.org/browse/XWIKI-22759
* https://jira.xwiki.org/browse/XWIKI-22758
* https://jira.xwiki.org/browse/XWIKI-22799
* https://github.com/xwiki/xwiki-platform/commit/abdcefc0db27035b67329add836fd683e0cf92b8
* https://github.com/xwiki/xwiki-platform/commit/cc74dc802efe0e2d3fa2ba3355dbadc51c5fd8c7
* https://github.com/xwiki/xwiki-platform/commit/0a705e8e253cb871b804e25c53b2bde879c886bd
* https://github.com/xwiki/xwiki-platform/commit/3d451e957fe2b14459e9ac64172b4a0e4c46971c

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-c32m-27pj-4xcj
- https://nvd.nist.gov/vuln/detail/CVE-2025-49582
- https://github.com/xwiki/xwiki-platform/commit/0a705e8e253cb871b804e25c53b2bde879c886bd
- https://github.com/xwiki/xwiki-platform/commit/3d451e957fe2b14459e9ac64172b4a0e4c46971c
- https://github.com/xwiki/xwiki-platform/commit/abdcefc0db27035b67329add836fd683e0cf92b8
- https://github.com/xwiki/xwiki-platform/commit/cc74dc802efe0e2d3fa2ba3355dbadc51c5fd8c7
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-22758
- https://jira.xwiki.org/browse/XWIKI-22759
- https://jira.xwiki.org/browse/XWIKI-22763
- https://jira.xwiki.org/browse/XWIKI-22799
