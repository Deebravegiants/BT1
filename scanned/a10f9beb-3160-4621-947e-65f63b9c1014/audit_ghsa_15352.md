# [C] XWiki Platform allows XSS through XClass name in string properties

## Summary
Severity: Critical
Advisory: GHSA-wcg9-pgqv-xm5v
CVE: CVE-2024-43400
CWE: CWE-79, CWE-96
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-08-19
Source: https://github.com/advisories/GHSA-wcg9-pgqv-xm5v
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=1.1.2 <14.10.21
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=15.0-rc-1 <15.5.5
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=15.6-rc-1 <15.10.6
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=16.0.0-rc-1 <16.0.0

## Details
### Impact
Is it possible for a user without Script or Programming rights to craft a URL pointing to a page with arbitrary JavaScript.
This requires social engineer to trick a user to follow the URL.

#### Reproduction steps

1. As a user without script or programming right, create a (non-terminal) document named `" + alert(1) + "` (the quotes need to be part of the name).
1. Edit the class.
1. Add a string property named `"test"`.
1. Edit using the object editor and add an object of the created class
1. Get an admin to open `<xwiki-server>/xwiki/bin/view/%22%20%2B%20alert(1)%20%2B%20%22/?viewer=display&type=object&property=%22%20%2B%20alert(1)%20%2B%20%22.WebHome.test&mode=edit` where `<xwiki-server>` is the URL of your XWiki installation.

### Patches
This has been patched in XWiki 14.10.21, 15.5.5, 15.10.6 and 16.0.0.

### Workarounds

We're not aware of any workaround except upgrading.

### References
- https://jira.xwiki.org/browse/XWIKI-21810
- https://github.com/xwiki/xwiki-platform/commit/27eca8423fc1ad177518077a733076821268509c

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-wcg9-pgqv-xm5v
- https://nvd.nist.gov/vuln/detail/CVE-2024-43400
- https://github.com/xwiki/xwiki-platform/commit/27eca8423fc1ad177518077a733076821268509c
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-21810
