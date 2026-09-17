# [M] BuddyPress: Any authenticated attacker can enumerate another user's complete friend list via IDOR

## Summary
Severity: Medium
Advisory: GHSA-wmjr-58rf-xgrc
CVE: CVE-2026-53675
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-wmjr-58rf-xgrc
Type: github-advisory

## Affected
- Packagist: `buddypress/buddypress` — affected >=0

## Details
BuddyPress 14.4.0 contains an insecure direct object reference vulnerability in the friends REST API that allows any authenticated attacker to enumerate another user's complete friend list. Attackers can query the friends endpoint with an arbitrary user_id because the get_items_permissions_check method only verifies that the requester is logged in and never checks ownership of the requested list, resulting in disclosure of users' private social connections.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-53675
- https://buddypress.org
- https://github.com/buddypress/BuddyPress
- https://wordpress.org/plugins/buddypress
- https://www.vulncheck.com/advisories/buddypress-friends-list-idor-via-rest-api
