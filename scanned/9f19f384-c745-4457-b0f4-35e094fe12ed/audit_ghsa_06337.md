# [H] XWiki Platform Live Data Live Table Connector has privilege escalation from edit to script right through Live Data editing

## Summary
Severity: High
Advisory: GHSA-45ph-gxxr-gwgw
CVE: CVE-2026-53966
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-19
Source: https://github.com/advisories/GHSA-45ph-gxxr-gwgw
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-livedata-livetable` — affected >=13.4-rc-1 <16.10.17
- Maven: `org.xwiki.platform:xwiki-platform-livedata-livetable` — affected >=17.0.0-rc-1 <17.4.10
- Maven: `org.xwiki.platform:xwiki-platform-livedata-livetable` — affected >=17.5.0-rc-1 <17.10.4
- Maven: `org.xwiki.platform:xwiki-platform-livedata-livetable` — affected >=18.0.0-rc-1 <18.1.0-rc-1

## Details
### Impact
Any user who can edit a page in XWiki can use Live Data's edit REST API in XWiki to change the rights on that page. This allows the user to obtain script right on the page. Script right allows the user to execute potentially dangerous Velocity scripts and send unfiltered HTML and JavaScript to the client. If there are other security checks, e.g., in extensions, implemented as listeners to `UserUpdatingDocumentEvent` and similar `User…` events, these checks can be circumvented, too.

### Patches
This vulnerability has been patched by properly calling all checks in Live Data in XWiki 16.10.17, 17.4.10, 17.10.4 and 18.1.0.

### Workarounds
We're not aware of any workarounds apart from upgrading.

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-45ph-gxxr-gwgw
- https://github.com/xwiki/xwiki-platform/commit/448b0f074cc6711410eb2647c4740454c92d1626
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-23986
