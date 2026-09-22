# [H] OPNsense has an LDAP Injection via Unsanitized Username in Authentication

## Summary
Severity: High
Advisory: CVE-2026-34578
Aliases: GHSA-jpm7-f59c-mp54
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-04-09
Source: https://osv.dev/vulnerability/CVE-2026-34578
Type: osv

## Details
OPNsense is a FreeBSD based firewall and routing platform. Prior to 26.1.6, OPNsense's LDAP authentication connector passes the login username directly into an LDAP search filter without calling ldap_escape(). An unauthenticated attacker can inject LDAP filter metacharacters into the username field of the WebGUI login page to enumerate valid LDAP usernames in the configured directory. When the LDAP server configuration includes an Extended Query to restrict login to members of a specific group, the same injection can be used to bypass that group membership restriction and authenticate as any LDAP user whose password is known, regardless of group membership. This vulnerability is fixed in 26.1.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34578.json
- https://github.com/opnsense/core/security/advisories/GHSA-jpm7-f59c-mp54
- https://nvd.nist.gov/vuln/detail/CVE-2026-34578
- https://github.com/opnsense/core/commit/016f66cb4620cd48183fa97843f343bb71813c6e
