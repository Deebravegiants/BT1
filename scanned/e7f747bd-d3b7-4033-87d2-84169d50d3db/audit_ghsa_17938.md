# [M] XWiki allows Reflected XSS in two templates

## Summary
Severity: Medium
Advisory: GHSA-m9x4-w7p9-mxhx
CVE: CVE-2025-32430
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-08-05
Source: https://github.com/advisories/GHSA-m9x4-w7p9-mxhx
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-web-templates` — affected >=4.2-milestone-3 <16.4.8
- Maven: `org.xwiki.platform:xwiki-platform-web-templates` — affected >=16.5.0-rc-1 <16.10.6
- Maven: `org.xwiki.platform:xwiki-platform-web-templates` — affected >=17.0.0-rc-1 <17.3.0-rc-1

## Details
### Impact
Reflected XSS vulnerabilities in two templates allow an attacker to execute malicious JavaScript code in the context of the victim's session by getting the victim to visit an attacker-controlled URL. PoC URLs are `/xwiki/bin/view/Main/?xpage=job_status_json&jobId=asdf&translationPrefix=<img src=1 onerror=alert(document.domain)>` and `/xwiki/bin/view/Main/?xpage=distribution&extensionId=%3Cimg src=x onerror=alert(document.domain)%3E&extensionVersionConstraint=%3Cimg src=x onerror=alert(document.domain)%3E`. This allows the attacker to perform arbitrary actions using the permissions of the victim.

### Patches
The problem has been patched in XWiki 16.4.8, 16.10.6 and 17.3.0RC1 by adding escaping in the affected templates.

### Workarounds
The affected templates can be patched manually in the WAR by applying the same changes as in [the patch](https://github.com/xwiki/xwiki-platform/commit/e5926a938cbecc8b1eaa48053d8d370cff107cb0).

### Attribution

The vulnerability involving `job_status_json` has been reported as "Unauth Reflected XSS" vulnerability by Aleksey Solovev (Positive Technologies), and the vulnerability involving `distribution` has been reported as "Auth Admin Reflected XSS" vulnerability by Evgeny Kopytin (Positive Technologies). According to our analysis, both vulnerabilities can be exploited against both unauthenticated and authenticated victims (including victims with admin privileges) which is why we publish them together in this advisory.

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-m9x4-w7p9-mxhx
- https://nvd.nist.gov/vuln/detail/CVE-2025-32430
- https://github.com/xwiki/xwiki-platform/commit/e5926a938cbecc8b1eaa48053d8d370cff107cb0
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-23096
