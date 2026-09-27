# [H] Apache CloudStack: SAML Signature Exclusion

## Summary
Severity: High
Advisory: CVE-2024-41107
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-19
Source: https://osv.dev/vulnerability/CVE-2024-41107
Type: osv

## Details
The CloudStack SAML authentication (disabled by default) does not enforce signature check. In CloudStack environments where SAML authentication is enabled, an attacker that initiates CloudStack SAML single sign-on authentication can bypass SAML authentication by submitting a spoofed SAML response with no signature and known or guessed username and other user details of a SAML-enabled CloudStack user-account. In such environments, this can result in a complete compromise of the resources owned and/or accessible by a SAML enabled user-account.

Affected users are recommended to disable the SAML authentication plugin by setting the "saml2.enabled" global setting to "false", or upgrade to version 4.18.2.2, 4.19.1.0 or later, which addresses this issue.

## References
- http://www.openwall.com/lists/oss-security/2024/07/19/1
- http://www.openwall.com/lists/oss-security/2024/07/19/2
- https://cloudstack.apache.org/blog/security-release-advisory-cve-2024-41107
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41107.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41107
- https://www.shapeblue.com/shapeblue-security-advisory-apache-cloudstack-cve-2024-41107
- https://github.com/apache/cloudstack/issues/4519
- https://lists.apache.org/thread/5q06g8zvmhcw6w3tjr6r5prqdw6zckg3
