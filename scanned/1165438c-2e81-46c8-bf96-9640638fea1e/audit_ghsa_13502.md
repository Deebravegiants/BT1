# [C] XWiki Identity Oauth Privilege escalation (PR)/remote code execution from login screen through unescaped URL parameter

## Summary
Severity: Critical
Advisory: GHSA-h2rm-29ch-wfmh
CVE: CVE-2023-45144
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-10-17
Source: https://github.com/advisories/GHSA-h2rm-29ch-wfmh
Type: github-advisory

## Affected
- Maven: `com.xwiki.identity-oauth:identity-oauth-ui` — affected >=1.0 <1.6

## Details
### Impact

When login via the OAuth method, the identityOAuth parameters, sent in a GET request is vulnerable to XSS and XWiki syntax injection. This allows remote code execution via the groovy macro and thus affects the confidentiality, integrity and availability of the whole XWiki installation. 

The vulnerability is in [this part](https://github.com/xwikisas/identity-oauth/blob/master/ui/src/main/resources/IdentityOAuth/LoginUIExtension.vm#L58) of the code.

### Patches
The issue has been fixed in Identity OAuth version 1.6 by https://github.com/xwikisas/identity-oauth/commit/d805d3154b17c6bf455ddf5deb0a3461a3833bc6 . The fix is in the content of the [IdentityOAuth/LoginUIExtension](https://github.com/xwikisas/identity-oauth/commit/d805d3154b17c6bf455ddf5deb0a3461a3833bc6#diff-2ab2e0716443d790d7d798320e4a45151661f4eca5440331f4a227b29c87c188) file

### Workarounds
There are no known workarounds besides upgrading.

### References
_Are there any links users can visit to find out more?_

* Original report: https://jira.xwiki.org/browse/XWIKI-20719

## References
- https://github.com/xwikisas/identity-oauth/security/advisories/GHSA-h2rm-29ch-wfmh
- https://nvd.nist.gov/vuln/detail/CVE-2023-45144
- https://github.com/xwikisas/identity-oauth/commit/d805d3154b17c6bf455ddf5deb0a3461a3833bc6
- https://github.com/xwikisas/identity-oauth/commit/d805d3154b17c6bf455ddf5deb0a3461a3833bc6#diff-2ab2e0716443d790d7d798320e4a45151661f4eca5440331f4a227b29c87c188
- https://github.com/xwikisas/identity-oauth
- https://github.com/xwikisas/identity-oauth/blob/master/ui/src/main/resources/IdentityOAuth/LoginUIExtension.vm#L58
- https://jira.xwiki.org/browse/XWIKI-20719
