# [M] CVE-2021-32729

## Summary
Severity: Medium
Advisory: CVE-2021-32729
Aliases: GHSA-m738-3rc4-5xv3
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2021-07-01
Source: https://osv.dev/vulnerability/CVE-2021-32729
Type: osv

## Details
XWiki Platform is a generic wiki platform offering runtime services for applications built on top of it. A vulnerability exists in versions prior to 12.6.88, 12.10.4, and 13.0. The script service method used to reset the authentication failures record can be executed by any user with Script rights and does not require Programming rights. An attacher with script rights who is able to reset the authentication failure record might perform a brute force attack, since they would be able to virtually deactivate the mechanism introduced to mitigate those attacks. The problem has been patched in version 12.6.8, 12.10.4 and 13.0. There are no workarounds aside from upgrading.

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-m738-3rc4-5xv3
- https://jira.xwiki.org/browse/XWIKI-18276
