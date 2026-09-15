# [H] Bundled ldap-authentication-plugin fails to neutralise LDAP special elements in usernames

## Summary
Severity: High
Advisory: CVE-2022-24832
Aliases: GHSA-x5v3-x9qj-mh3h
CVSS: 8.2 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2022-04-11
Source: https://osv.dev/vulnerability/CVE-2022-24832
Type: osv

## Details
GoCD is an open source a continuous delivery server. The bundled gocd-ldap-authentication-plugin included with the GoCD Server fails to correctly escape special characters when using the username to construct LDAP queries. While this does not directly allow arbitrary LDAP data exfiltration, it can allow an existing LDAP-authenticated GoCD user with malicious intent to construct and execute malicious queries, allowing them to deduce facts about other users or entries within the LDAP database (e.g alternate fields, usernames, hashed passwords etc) through brute force mechanisms. This only affects users who have a working LDAP authorization configuration enabled on their GoCD server, and only is exploitable by users authenticating using such an LDAP configuration. This issue has been fixed in GoCD 22.1.0, which is bundled with gocd-ldap-authentication-plugin v2.2.0-144.

## References
- https://docs.gocd.org/22.1.0/configuration/dev_authentication.html#ldapad-authentication
- https://github.com/gocd/gocd-ldap-authentication-plugin/releases/tag/v2.2.0-144
- https://github.com/gocd/gocd/releases/tag/22.1.0
- https://www.gocd.org/releases/#22-1-0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24832.json
- https://github.com/gocd/gocd/security/advisories/GHSA-x5v3-x9qj-mh3h
- https://nvd.nist.gov/vuln/detail/CVE-2022-24832
- https://github.com/gocd/gocd-ldap-authentication-plugin/commit/87fa7dac5d899b3960ab48e151881da4793cfcc3
- https://github.com/gocd/gocd/pull/10244
- https://github.com/gocd/gocd-ldap-authentication-plugin
