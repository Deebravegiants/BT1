# [H] Parse Server's custom object ID allows to acquire role privileges

## Summary
Severity: High
Advisory: GHSA-8xq9-g7ch-35hg
CVE: CVE-2024-47183
CWE: CWE-285, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-10-04
Source: https://github.com/advisories/GHSA-8xq9-g7ch-35hg
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=0 <6.5.9
- npm: `parse-server` — affected >=7.0.0 <7.3.0

## Details
### Impact

If the Parse Server option `allowCustomObjectId: true` is set, an attacker that is allowed to create a new user can set a custom object ID for that new user that exploits the vulnerability and acquires privileges of a specific role.

### Patches

Improved validation for custom user object IDs. Session tokens for existing users with an object ID that exploits the vulnerability are now rejected.

### Workarounds

- Disable custom object IDs by setting `allowCustomObjectId: false` or not setting the option which defaults to `false`.
- Use a Cloud Code Trigger to validate that a new user's object ID doesn't start with the prefix `role:`.

### References

- https://github.com/parse-community/parse-server/security/advisories/GHSA-8xq9-g7ch-35hg
- https://github.com/parse-community/parse-server/pull/9317 (fix for Parse Server 7)
- https://github.com/parse-community/parse-server/pull/9318 (fix for Parse Server 6)

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-8xq9-g7ch-35hg
- https://nvd.nist.gov/vuln/detail/CVE-2024-47183
- https://github.com/parse-community/parse-server/pull/9317
- https://github.com/parse-community/parse-server/pull/9318
- https://github.com/parse-community/parse-server/commit/13ee52f0d19ef3a3524b3d79aea100e587eb3cfc
- https://github.com/parse-community/parse-server/commit/1bfbccf9ee7ea77533b2b2aa7c4c69f3bd35e66f
- https://github.com/parse-community/parse-server
