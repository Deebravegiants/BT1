# [H] XWiki allows privilege escalation through link refactoring

## Summary
Severity: High
Advisory: GHSA-jm43-hrq7-r7w6
CVE: CVE-2025-49580
CWE: CWE-266
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-06-13
Source: https://github.com/advisories/GHSA-jm43-hrq7-r7w6
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-refactoring-default` — affected >=17.0.0-rc-1 <17.1.0-rc-1
- Maven: `org.xwiki.platform:xwiki-platform-refactoring-default` — affected >=16.5.0-rc-1 <16.10.4
- Maven: `org.xwiki.platform:xwiki-platform-refactoring-default` — affected >=8.2 <16.4.7
- Maven: `org.xwiki.platform:xwiki-platform-refactoring-default` — affected >=7.4.5 <16.4.7

## Details
### Impact

Pages can gain script or programming rights when they contain a link and the target of the link is renamed or moved. This might lead to execution of scripts contained in xobjects that should have never been executed. 
This vulnerability affects all version of XWiki since 8.2 and 7.4.5.

### Patches

The patch consists in only setting the `originalMetadataAuthor` when performing such change, so that it's displayed in the history but it has no impact on the right evaluation (i.e. the original author of the changes is still used for right computation). 

This patch has been applied on XWiki 16.4.7, 17.1.0RC1, 16.10.4.

### Workarounds

There's no workaround for this vulnerability, except preventing to perform any refactoring operation with users having more than edit rights. 
Administrators are strongly advised to upgrade. If not possible, the patch only impacts module `xwiki-platform-refactoring-default` so it's possible to apply the commit and rebuild and deploy only that module.

### CVSS explanation

Attack vector: Network - Always for XWiki.
Complexity: Low - The set of operations to perform the attack is quite easy.
Attack requirements: None - Any system is vulnerable, it doesn't depend on specific condition other than user interaction.
Privileges required: Low - The attacker only needs edit rights.
User interaction: Active - To be successful the attack needs someone with more rights to perform a move/rename of a specific page.
Confidentiality: High - The attack might lead to execution of any script.
Integrity: High - The attack might lead to execution of any script.
Availability: High - The attack might lead to execution of any script.
Subsequent system impacts: None for any criteria. Only current system is affected.

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-jm43-hrq7-r7w6
- https://nvd.nist.gov/vuln/detail/CVE-2025-49580
- https://github.com/xwiki/xwiki-platform/commit/ab209acd780da69a4c5ff77ff011efd698273cec
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-22836
