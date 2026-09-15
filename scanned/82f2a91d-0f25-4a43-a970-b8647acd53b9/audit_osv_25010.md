# [C] Code injection from view right using Invitation.InvitationCommon in xwiki-platform

## Summary
Severity: Critical
Advisory: CVE-2023-29518
Aliases: GHSA-px54-3w5j-qjg9
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L)
Published: 2023-04-18
Source: https://osv.dev/vulnerability/CVE-2023-29518
Type: osv

## Details
XWiki Platform is a generic wiki platform offering runtime services for applications built on top of it. Any user with view rights can execute arbitrary Groovy, Python or Velocity code in XWiki leading to full access to the XWiki installation. The root cause is improper escaping of `Invitation.InvitationCommon`. This page is installed by default. The vulnerability has been patched in XWiki 15.0-rc-1, 14.10.1, 14.4.8, and 13.10.11. Users are advised to upgrade. There are no known workarounds for this issue.

## References
- https://jira.xwiki.org/browse/XWIKI-20283
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/29xxx/CVE-2023-29518.json
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-px54-3w5j-qjg9
- https://nvd.nist.gov/vuln/detail/CVE-2023-29518
- https://github.com/xwiki/xwiki-platform/commit/3d055a0a5ec42fdebce4d71ee98f94553fdbfebf
