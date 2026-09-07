# [H] Passbolt API Stored XSS on first/last name during setup

## Summary
Severity: High
Advisory: GHSA-2f46-4xjm-73x5
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-20
Source: https://github.com/advisories/GHSA-2f46-4xjm-73x5
Type: github-advisory

## Affected
- Packagist: `passbolt/passbolt_api` — affected >=0 <2.11.0

## Details
### Description
An administrator can craft a user with a malicious first name and last name, using a payload such as
```
<svg onload="confirm(document.domain)">'); ?></svg>
```
The user will then receive the invitation email and click on the setup link. The setup start page served by the server will fire the XSS.

### Impact of issue
An administrator could use this exploit to edit the setup start page for a given user, for example, trick the user into installing another extension. Even though the severity of this issue in itself is high, the likelihood is low because the exploit will be visible in clear by the user in the email notification, and also requires an action from a malicious administrator.

### Fix
Sanitize the firstname and lastname in the page that is used to trigger the extension setup process.

Additionally since v2.11 some default CSP are inserted in the server response headers to prevent inline-scripts or 3rd party domain scripts on pages served by the passbolt API. This is to cater for the case where the administrator has not set them up as part of the web server configuration.

## References
- https://github.com/passbolt/passbolt_api/commit/6135b483f72c6853e6085e329f5f8d7be60c9933
- https://github.com/FriendsOfPHP/security-advisories/blob/master/passbolt/passbolt_api/2019-08-07-1.yaml
- https://github.com/passbolt/passbolt_api
- https://github.com/passbolt/passbolt_api/blob/master/CHANGELOG.md#2110---2019-08-08
- https://www.passbolt.com/incidents/20190807_multiple_vulnerabilities
