# [M] org.xwiki.platform:xwiki-platform-wysiwyg-api Open Redirect vulnerability

## Summary
Severity: Medium
Advisory: GHSA-pjhg-9wr9-rj96
CVE: CVE-2025-32970
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-04-29
Source: https://github.com/advisories/GHSA-pjhg-9wr9-rj96
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-wysiwyg-api` — affected >=13.5-rc-1 <15.10.13
- Maven: `org.xwiki.platform:xwiki-platform-wysiwyg-api` — affected >=16.0.0-rc-1 <16.4.4
- Maven: `org.xwiki.platform:xwiki-platform-wysiwyg-api` — affected >=16.5.0-rc-1 <16.8.0

## Details
### Impact

An open redirect vulnerability in the HTML conversion request filter allows attackers to construct URLs on an XWiki instance that redirect to any URL. To reproduce, open `<xwiki-host>/xwiki/bin/view/Main/?foo=bar&foo_syntax=invalid&RequiresHTMLConversion=foo&xerror=https://www.example.com/` where `<xwiki-host>` is the URL of your XWiki installation.

### Patches
This bug has been fixed in XWiki 15.10.13, 16.4.4 and 16.8.0 by validating the domain of the redirect URL against the configured safe domains and the current request's domain.

### Workarounds
A web application firewall could be configured to reject requests with the `xerror` parameter as from our analysis this parameter isn't used anymore. For requests with the `RequiresHTMLConversion` parameter set, the referrer URL should be checked if it points to the XWiki installation. Apart from that, we're not aware of any workarounds.

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-pjhg-9wr9-rj96
- https://nvd.nist.gov/vuln/detail/CVE-2025-32970
- https://github.com/xwiki/xwiki-platform/commit/6dab7909f45deb00efd36a0cd47788e95ad64802
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-22487
