# [M] parse-server's session object properties can be updated by foreign user if object ID is known

## Summary
Severity: Medium
Advisory: GHSA-6w4q-23cf-j9jp
CVE: CVE-2022-39225
CWE: CWE-276, CWE-669
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-09-21
Source: https://github.com/advisories/GHSA-6w4q-23cf-j9jp
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=0 <4.10.15
- npm: `parse-server` — affected >=5.0.0 <5.2.6

## Details
### Impact

A foreign user can write to the session object of another user if the session object ID is known. For example, a foreign user can assign the session object to their own user by writing to the `user` field and then read any custom fields of that session object.

Note that assigning a session to a foreign user does not usually change the privileges of neither of the two users, according to how Parse Server uses session objects internally. However, if custom logic is used to relate specific session objects to privileges this vulnerability may have a higher level of severity.

The vulnerability does not allow a foreign user to assign a session object to themselves, read the session token, and then reassign the session object to the original user to then authenticate as that user with the known session token. The vulnerability only exists for foreign session objects, a user cannot assign their own session to another user.

While it is unlikely that the session object ID of another user is known, it is possible to brute-force guess an object ID, even though the attacker would not know to which user a successfully guessed session object ID belongs.

### Patches

The fix prevents writing to foreign session objects, even if the session object ID is known.

### Workarounds

Add a `beforeSave` trigger to the `_Session` class and prevent writing if the requesting user is different from the user in the session object.

### References

- GitHub advisory [GHSA-6w4q-23cf-j9jp](https://github.com/parse-community/parse-server/security/advisories/GHSA-6w4q-23cf-j9jp)

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-6w4q-23cf-j9jp
- https://nvd.nist.gov/vuln/detail/CVE-2022-39225
- https://github.com/parse-community/parse-server/commit/37fed3062ccc3ef1dfd49a9fc53318e72b3e4aff
- https://github.com/parse-community/parse-server
- https://github.com/parse-community/parse-server/releases/tag/4.10.15
- https://github.com/parse-community/parse-server/releases/tag/5.2.6
