# [M] XWiki Platform vulnerable to potential arbitrary file writing using path traversal from (subwiki) admin

## Summary
Severity: Medium
Advisory: GHSA-vgwr-23fq-pr7g
CVE: CVE-2026-48047
CWE: CWE-24
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:L/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-vgwr-23fq-pr7g
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-webjars-api` — affected >=9.6-rc-1 <16.10.17
- Maven: `org.xwiki.platform:xwiki-platform-webjars-api` — affected >=17.0.0-rc-1 <17.4.9
- Maven: `org.xwiki.platform:xwiki-platform-webjars-api` — affected >=17.5.0-rc-1 <17.10.3

## Details
### Impact
A potential path traversal vulnerability allow an attacker who manages to get a malicious WebJar extension installed on the wiki to write arbitrary files. While the consequences could be severe like overriding configuration files and setting the superadmin password, the attack first requires that the attacker already has admin access to at least a subwiki to be able to install a malicious extension. Further, the attacker needs to publish a malicious extension in an extension repository that is configured in the instance.

### Patches
This vulnerability has been patched in XWiki 16.10.17, 17.4.9, 17.10.3, and 18.0.0RC1.

### Workarounds
XWiki is not aware of any workarounds except for being careful whom developers grant script and admin rights to.

### Resources
* https://jira.xwiki.org/browse/XWIKI-23902
* https://github.com/xwiki/xwiki-platform/commit/9f747fcd3200259a1de51957d3f5f6acc8e3816c

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-vgwr-23fq-pr7g
- https://github.com/xwiki/xwiki-platform/commit/9f747fcd3200259a1de51957d3f5f6acc8e3816c
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-23902
