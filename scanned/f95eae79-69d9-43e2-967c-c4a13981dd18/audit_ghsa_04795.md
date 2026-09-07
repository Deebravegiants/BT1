# [H] BuddyPress: Authenticated attackers can access arbitrary private message threads via user_id request parameter

## Summary
Severity: High
Advisory: GHSA-j3j5-5m8v-7gvc
CVE: CVE-2026-53673
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-j3j5-5m8v-7gvc
Type: github-advisory

## Affected
- Packagist: `buddypress/buddypress` — affected >=0 <14.5.0

## Details
BuddyPress 14.4.0 contains an insecure direct object reference vulnerability in the messages REST API that allows authenticated attackers to access arbitrary private message threads by supplying a user_id parameter in the request. Attackers can pass another user's identifier to the get_item_permissions_check method, which validates the supplied user_id instead of the logged-in user and is reused by the update and delete handlers, to read, reply to, or delete any user's private messages.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-53673
- https://github.com/buddypress/buddypress/commit/27d41e9749a878103b3a673b37dfc92b7f8f2cb7
- https://buddypress.org
- https://github.com/buddypress/BuddyPress
- https://wordpress.org/plugins/buddypress
- https://www.vulncheck.com/advisories/buddypress-private-message-idor-via-rest-api-user-id-parameter
