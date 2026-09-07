# [H] BuddyPress privilege escalation via REST API

## Summary
Severity: High
Advisory: GHSA-m6j4-8r7p-wpp3
CVE: CVE-2021-21389
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-10-06
Source: https://github.com/advisories/GHSA-m6j4-8r7p-wpp3
Type: github-advisory

## Affected
- Packagist: `buddypress/buddypress` — affected >=5.0.0 <7.2.1

## Details
### Impact
It's possible for a non-privileged, regular user to obtain administrator rights by exploiting an issue in the BuddyPress REST API members endpoint.

### Patches
The vulnerability has been fixed in BuddyPress 7.2.1. Existing installations of the plugin should be updated to this version to mitigate the issue.

### References
https://buddypress.org/2021/03/buddypress-7-2-1-security-release/

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [HackerOne](https://hackerone.com/wordpress)

## References
- https://github.com/buddypress/BuddyPress/security/advisories/GHSA-m6j4-8r7p-wpp3
- https://nvd.nist.gov/vuln/detail/CVE-2021-21389
- https://buddypress.org/2021/03/buddypress-7-2-1-security-release
- https://codex.buddypress.org/releases/version-7-2-1
- https://github.com/buddypress/BuddyPress
