# [C] XWiki Platform privilege escalation (PR)/RCE from account through Invitation subject/message

## Summary
Severity: Critical
Advisory: GHSA-7954-6m9q-gpvf
CVE: CVE-2023-37914
CWE: CWE-94, CWE-95
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2023-08-18
Source: https://github.com/advisories/GHSA-7954-6m9q-gpvf
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-invitation-ui` — affected >=2.5-m-1 <14.4.8
- Maven: `org.xwiki.platform:xwiki-platform-invitation-ui` — affected >=14.5 <14.10.6
- Maven: `org.xwiki.platform:xwiki-platform-invitation-ui` — affected >=15.0-rc-1 <15.2-rc-1

## Details
### Impact
Any user who can view `Invitation.WebHome` can execute arbitrary script macros including Groovy and Python macros that allow remote code execution including unrestricted read and write access to all wiki contents. This can be reproduced with the following steps:


1.    Open the invitation application (Invitation.WebHome).
1.    Set the subject to `{{cache}}{{groovy}}new File("/tmp/exploit.txt").withWriter { out -> out.println("Attacked from invitation!"); }{{/groovy}}{{/cache}}`
1.    Click "Preview"


### Patches
The vulnerability has been patched on XWiki 14.4.8, 15.2-rc-1, and 14.10.6.

### Workarounds
The vulnerability can be patched manually by applying the [patch](https://github.com/xwiki/xwiki-platform/commit/ff1d8a1790c6ee534c6a4478360a06efeb2d3591) on `Invitation.InvitationCommon` and `Invitation.InvitationConfig`.

### References
- https://jira.xwiki.org/browse/XWIKI-20421
- https://github.com/xwiki/xwiki-platform/commit/ff1d8a1790c6ee534c6a4478360a06efeb2d3591

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-7954-6m9q-gpvf
- https://nvd.nist.gov/vuln/detail/CVE-2023-37914
- https://github.com/xwiki/xwiki-platform/commit/ff1d8a1790c6ee534c6a4478360a06efeb2d3591
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20421
