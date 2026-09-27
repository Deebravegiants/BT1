# [C] org.xwiki.platform:xwiki-platform-flamingo-theme-ui Eval Injection vulnerability

## Summary
Severity: Critical
Advisory: CVE-2023-26477
Aliases: GHSA-x2qm-r4wx-8gpg
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2023-03-02
Source: https://osv.dev/vulnerability/CVE-2023-26477
Type: osv

## Details
XWiki Platform is a generic wiki platform. Starting in versions 6.3-rc-1 and 6.2.4, it's possible to inject arbitrary wiki syntax including Groovy, Python and Velocity script macros via the `newThemeName` request parameter (URL parameter), in combination with additional parameters. This has been patched in the supported versions 13.10.10, 14.9-rc-1, and 14.4.6. As a workaround, it is possible to edit `FlamingoThemesCode.WebHomeSheet` and manually perform the changes from the patch fixing the issue.

## References
- https://jira.xwiki.org/browse/XWIKI-19757
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/26xxx/CVE-2023-26477.json
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-x2qm-r4wx-8gpg
- https://nvd.nist.gov/vuln/detail/CVE-2023-26477
- https://github.com/xwiki/xwiki-platform/commit/ea2e615f50a918802fd60b09ec87aa04bc6ea8e2#diff-e2153fa59f9d92ef67b0afbf27984bd17170921a3b558fac227160003d0dfd2aR283-R284
