# [H] XWiki's REST APIs don't enforce any limits, leading to unavailability and OOM in large wikis

## Summary
Severity: High
Advisory: GHSA-cc84-q3v3-mhgf
CVE: CVE-2025-66473
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-12-10
Source: https://github.com/advisories/GHSA-cc84-q3v3-mhgf
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-rest-server` — affected >=0 <16.10.11
- Maven: `org.xwiki.platform:xwiki-platform-rest-server` — affected >=17.0.0-rc-1 <17.4.4
- Maven: `org.xwiki.platform:xwiki-platform-rest-server` — affected >=17.5.0-rc-1 <17.7.0-rc-1

## Details
### Impact
XWiki's REST API doesn't enforce any limits for the number of items that can be requested in a single request at the moment. Depending on the number of pages in the wiki and the memory configuration, this can lead to slowness and unavailability of the wiki. As an example, the `/rest/wikis/xwiki/spaces` resource returns all spaces on the wiki by default, which are basically all pages.

### Patches
XWiki 17.7.0RC1, 17.4.4 and 16.10.11 introduce a configurable limit, limiting responses to 1000 items by default. Requesting larger limits leads to an error now.

### Workarounds
We're not aware of any workaround, except denying access to the affected REST resources in a proxy in front of XWiki.

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-cc84-q3v3-mhgf
- https://nvd.nist.gov/vuln/detail/CVE-2025-66473
- https://github.com/xwiki/xwiki-platform/commit/e3c47745195fb445b054537be86f5c01ee69558b
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-23355
