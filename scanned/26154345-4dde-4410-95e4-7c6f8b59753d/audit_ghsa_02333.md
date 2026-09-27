# [M] parse-server new anonymous user session acts as if it's created with password

## Summary
Severity: Medium
Advisory: GHSA-23r4-5mxp-c7g5
CVE: CVE-2021-39138
CWE: CWE-287, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2021-08-23
Source: https://github.com/advisories/GHSA-23r4-5mxp-c7g5
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=0 <4.5.2

## Details
### Impact

Developers that use the REST API to signup users and also allow users to login anonymously. When an anonymous user is first signed up using REST, the server creates session incorrectly, particularly the `authProvider` field in `_Session` class under `createdWith` shows the user logged in creating a password. If a developer later depends on the `createdWith` field to provide a different level of access between a password user and anonymous user, the server incorrectly classified the session type as being created with a `password`.

The server currently doesn't use `createdWith` to make decisions on how things work internally, so if a developer isn't using `createdWith` directly, there's nothing to worry about. The vulnerability only affects users who depend on `createdWith` by using it directly.   

### Patches
Upgrade to version 4.5.1.

### Workarounds
Don't use the `createdWith` Session field to make decisions if you allow anonymous login.

### References
n/a

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-23r4-5mxp-c7g5
- https://nvd.nist.gov/vuln/detail/CVE-2021-39138
- https://github.com/parse-community/parse-server/commit/147bd9a3dc43391e92c36e05d5db860b04ca27db
- https://github.com/parse-community/parse-server
- https://github.com/parse-community/parse-server/releases/tag/4.5.2
