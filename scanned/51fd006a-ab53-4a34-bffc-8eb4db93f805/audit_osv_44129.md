# [H] Various Newfold Plugins Various Versions - Unauthenticated Authentication Bypass via Bearer Token Validation with Empty Secret

## Summary
Severity: High
Advisory: CVE-2026-80099
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-80099
Type: osv

## Details
Several Newfold plugins are vulnerable to Authentication Bypass. The vulnerability exists because the plugins bundle the wp-module-data module. In the module, the `authenticate()` method — registered on the `rest_authentication_errors` filter and therefore evaluated for every unauthenticated REST API request — performs an HMAC-style Bearer token comparison that degenerates when `HiiveConnection::get_auth_token()` returns `false`: PHP coerces `strrev(false)` to `strrev('')`, collapsing the secret salt to the publicly known constant `hash('sha256', '') = e3b0c44...`, while all remaining hash inputs (HTTP method, request URL, raw request body, and the `X-Timestamp` header) remain fully attacker-controlled. This makes it possible for unauthenticated attackers to compute a valid Bearer token entirely offline, pass the token equality check, and have `wp_set_current_user()` invoked against the first administrator returned by `get_users(['role' => 'administrator'])`, granting full administrator-level access and enabling arbitrary REST API operations such as creating new administrator accounts and achieving complete site takeover. Vulnerable versions are WP Plugin Crazy Domains (<= 2.5.2), WP Plugin Web (<= 2.3.4), WP Plugin Hostgator (<= 3.1.0), WP Plugin Bluehost (<= 4.17.1). The affected module is vulnerable in versions up to, and including, 2.9.4.

## References
- https://github.com/newfold-labs/wp-plugin-bluehost/compare/4.19.0...4.19.1
- https://github.com/newfold-labs/wp-plugin-crazy-domains/compare/2.5.2...2.5.3
- https://github.com/newfold-labs/wp-plugin-hostgator/compare/3.2.0...3.2.1
- https://github.com/newfold-labs/wp-plugin-web/compare/2.3.5...2.3.6
- https://plugins.trac.wordpress.org/browser/wp-module-data/trunk/includes/Data.php#L191
- https://plugins.trac.wordpress.org/browser/wp-module-data/trunk/includes/Data.php#L201
- https://plugins.trac.wordpress.org/browser/wp-module-data/trunk/includes/Data.php#L222
- https://plugins.trac.wordpress.org/browser/wp-module-data/trunk/includes/Data.php#L69
- https://plugins.trac.wordpress.org/browser/wp-module-data/trunk/includes/HiiveConnection.php#L406
- https://www.wordfence.com/threat-intel/vulnerabilities/id/3ee369c0-0d7c-4142-b3ba-a518288647ba?source=cve
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80099.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80099
- https://github.com/newfold-labs/wp-module-data/commit/9d913fd8fa12796c4d9c09081e4aeccfa5cb1301
