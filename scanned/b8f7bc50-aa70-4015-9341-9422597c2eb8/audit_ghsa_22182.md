# [M] XWiki Remote Code Execution

## Summary
Severity: Medium
Advisory: GHSA-h5jm-jjgx-q2wf
CVE: CVE-2006-7223
Ecosystem: Maven
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-h5jm-jjgx-q2wf
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=0.9.543 <1.0B1

## Details
PreviewAction in XWiki 0.9.543 through 0.9.1252 does not set the Author field to the identity of the user who last modified a document, which allows remote authenticated users without programming rights to execute arbitrary code by selecting a document whose author has programming rights, modifying this document to contain a script, and previewing without saving the document.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2006-7223
- https://github.com/xwiki/xwiki-platform/commit/c44172a3556d12b62c0d793ab18475e5e13d7120
- https://github.com/xwiki/xwiki-platform
- https://web.archive.org/web/20080616064908/http://jira.xwiki.org/jira/browse/XWIKI-366
