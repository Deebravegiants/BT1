# [C] org.xwiki.platform:xwiki-platform-notifications-ui Eval Injection vulnerability

## Summary
Severity: Critical
Advisory: CVE-2023-29210
Aliases: GHSA-p9mj-v5mf-m82x
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2023-04-15
Source: https://osv.dev/vulnerability/CVE-2023-29210
Type: osv

## Details
XWiki Commons are technical libraries common to several other top level XWiki projects. Any user with view rights on commonly accessible documents including the notification preferences macros can execute arbitrary Groovy, Python or Velocity code in XWiki leading to full access to the XWiki installation. The root cause is improper escaping of the user parameter of the macro that provide the notification filters. These macros are used in the user profiles and thus installed by default in XWiki. The vulnerability has been patched in XWiki 13.10.11, 14.4.7 and 14.10.

## References
- https://jira.xwiki.org/browse/XWIKI-20259
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/29xxx/CVE-2023-29210.json
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-p9mj-v5mf-m82x
- https://nvd.nist.gov/vuln/detail/CVE-2023-29210
- https://github.com/xwiki/xwiki-platform/commit/cebf9167e4fd64a8777781fc56461e9abbe0b32a
