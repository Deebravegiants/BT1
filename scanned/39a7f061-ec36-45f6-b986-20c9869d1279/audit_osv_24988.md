# [C] org.xwiki.platform:xwiki-platform-legacy-notification-activitymacro Eval Injection vulnerability

## Summary
Severity: Critical
Advisory: CVE-2023-29209
Aliases: GHSA-9pc2-x9qf-7j2q
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2023-04-15
Source: https://osv.dev/vulnerability/CVE-2023-29209
Type: osv

## Details
XWiki Commons are technical libraries common to several other top level XWiki projects. Any user with view rights on commonly accessible documents including the legacy notification activity macro can execute arbitrary Groovy, Python or Velocity code in XWiki leading to full access to the XWiki installation. The root cause is improper escaping of the macro parameters of the legacy notification activity macro. This macro is installed by default in XWiki. The vulnerability can be exploited via every wiki page that is editable including the user's profile, but also with just view rights using the HTMLConverter that is part of the CKEditor integration which is bundled with XWiki. The vulnerability has been patched in XWiki 13.10.11, 14.4.7 and 14.10.

## References
- https://jira.xwiki.org/browse/XWIKI-20258
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/29xxx/CVE-2023-29209.json
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-9pc2-x9qf-7j2q
- https://nvd.nist.gov/vuln/detail/CVE-2023-29209
- https://github.com/xwiki/xwiki-platform/commit/94392490884635c028199275db059a4f471e57bc
