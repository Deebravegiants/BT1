# [M] XWiki Platform Security Authorization Bridge allows users with just edit right can enforce required rights with programming right

## Summary
Severity: Medium
Advisory: GHSA-rhfv-688c-p6hp
CVE: CVE-2025-48063
CWE: CWE-285
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:L/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-05-21
Source: https://github.com/advisories/GHSA-rhfv-688c-p6hp
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-security-authorization-bridge` — affected >=16.10.0-rc-1 <16.10.4
- Maven: `org.xwiki.platform:xwiki-platform-security-authorization-bridge` — affected >=17.0.0-rc-1 <17.1.0-rc-1

## Details
### Impact
In XWiki 16.10.0, required rights were introduced as a way to limit which rights a document can have. Part of the security model of required rights is that a user who doesn't have a right also cannot define that right as required right. That way, users who are editing documents on which required rights are enforced can be sure that they're not giving a right to a script or object that it didn't have before. A bug in the implementation of the enforcement of this rule means that in fact, it was possible for any user with edit right on a document to set programming right as required right. If then a user with programming right edited that document, the content of that document would gain programming right, allowing remote code execution. This thereby defeats most of the security benefits of required rights. As XWiki still performs the required rights analysis when a user edits a page even when required rights are enforced, the user with programming right would still be warned about the dangerous content unless the attacker managed to bypass this check (see, e.g., https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-c32m-27pj-4xcj). Note also that none of the affected versions include a UI for enabling the enforcing of required rights so it seems unlikely that anybody relied on them for security in the affected versions. As this vulnerability provides no additional attack surface unless all documents in the wiki enforce required rights, we consider the impact of this attack to be low even though gaining programming right could have a high impact.

### Patches
This vulnerability has been patched in XWiki 16.10.4 and 17.1.0RC1.

### Workarounds
We're not aware of any workarounds except for upgrading.

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-rhfv-688c-p6hp
- https://nvd.nist.gov/vuln/detail/CVE-2025-48063
- https://github.com/xwiki/xwiki-platform/commit/2557813aef3b863988d6cca58de996e207086898
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-22859
