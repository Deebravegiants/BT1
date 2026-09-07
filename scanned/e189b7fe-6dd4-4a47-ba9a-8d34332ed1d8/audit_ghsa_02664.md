# [H] LiveQuery publishes user session tokens in parse-server

## Summary
Severity: High
Advisory: GHSA-7pr3-p5fm-8r9x
CVE: CVE-2021-41109
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-09-30
Source: https://github.com/advisories/GHSA-7pr3-p5fm-8r9x
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=0 <4.10.4

## Details
### Impact
For regular (non-LiveQuery) queries, the session token is removed from the response, but for LiveQuery payloads it is currently not. If a user has a LiveQuery subscription on the `Parse.User` class, all session tokens created during user sign-ups will be broadcast as part of the LiveQuery payload.

### Patches
Remove session token from LiveQuery payload.

### Workaround
Set `user.acl(new Parse.ACL())` in a beforeSave trigger to make the user private already on sign-up.

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-7pr3-p5fm-8r9x
- https://nvd.nist.gov/vuln/detail/CVE-2021-41109
- https://github.com/parse-community/parse-server/commit/4ac4b7f71002ed4fbedbb901db1f6ed1e9ac5559
- https://github.com/parse-community/parse-server
- https://github.com/parse-community/parse-server/releases/tag/4.10.4
