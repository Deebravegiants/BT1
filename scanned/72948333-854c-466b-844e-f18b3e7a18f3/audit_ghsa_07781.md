# [H] WireGuard Portal is Vulnerable to Privilege Escalation via User Self-Update to Admin Level

## Summary
Severity: High
Advisory: GHSA-5rmx-256w-8mj9
CVE: CVE-2026-27899
CWE: CWE-269, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-26
Source: https://github.com/advisories/GHSA-5rmx-256w-8mj9
Type: github-advisory

## Affected
- Go: `github.com/h44z/wg-portal` — affected >=0 <2.1.3

## Details
# Privilege Escalation to Admin via User Self-Update in wg-portal

## Summary

Any authenticated non-admin user can become a full administrator by sending a single PUT request to their own user profile endpoint with `"IsAdmin": true` in the JSON body. After logging out and back in, the session picks up admin privileges from the database.

Tested against wg-portal v2.1.2 (Docker image `wgportal/wg-portal:v2`).

## Root Cause

When a user updates their own profile, the server parses the full JSON body into the user model, including the `IsAdmin` boolean field. A function responsible for preserving calculated or protected attributes pins certain fields to their database values (such as base model data, linked peer count, and authentication data), but it does not do this for `IsAdmin`. As a result, whatever value the client sends for `IsAdmin` is written directly to the database.

## Impact

After the exploit, the attacker has full admin access to the WireGuard VPN management portal. They can:

- Read and modify every user account
- Create, modify, and delete WireGuard peers on any interface
- View WireGuard interface configurations
- Disable or lock other user accounts
- Access the full user list and their API tokens

## Patches
The problem was fixed in the latest release, [v2.1.3](https://github.com/h44z/wg-portal/releases/tag/v2.1.3). The [docker images](https://hub.docker.com/r/wgportal/wg-portal) for the tag 'latest' built from the master branch also include the fix.

## References
- https://github.com/h44z/wg-portal/security/advisories/GHSA-5rmx-256w-8mj9
- https://nvd.nist.gov/vuln/detail/CVE-2026-27899
- https://github.com/h44z/wg-portal/commit/fe4485037a25426446ced95050e9498f477bf71d
- https://github.com/h44z/wg-portal
- https://github.com/h44z/wg-portal/releases/tag/v2.1.3
- https://hub.docker.com/layers/wgportal/wg-portal/v2.1.3/images/sha256-39acfab55598a74e561828b8cb639515ddc222d6c884996111f5ef235aba9e7b
