# [C] Implementation trusts the "me" field returned by the authorization server without verifying it

## Summary
Severity: Critical
Advisory: GHSA-mjcr-rqjg-rhg3
CWE: CWE-290
Ecosystem: PyPI
Published: 2020-11-24
Source: https://github.com/advisories/GHSA-mjcr-rqjg-rhg3
Type: github-advisory

## Affected
- PyPI: `datasette-indieauth` — affected >=1.0 <1.1

## Details
### Impact

A malicious user can sign in as a user with any IndieAuth identifier. This is because the implementation does not verify that the final `"me"` URL value returned by the authorization server belongs to the same domain as the initial value entered by the user.

### Patches

Version 1.1 fixes this issue.

### Workarounds

There is no workaround. Upgrade to 1.1 immediately.

### References

- [Security Considerations: Differing User Profile URLs](https://indieauth.spec.indieweb.org/#differing-user-profile-urls-li-1) in the IndieAuth specification.

### For more information

If you have any questions or comments about this advisory:

* Open an issue in [simonw/datasette-indieauth](https://github.com/simonw/datasette-indieauth/issues)

## References
- https://github.com/simonw/datasette-indieauth/security/advisories/GHSA-mjcr-rqjg-rhg3
- https://github.com/simonw/datasette-indieauth/commit/376c8804c6b0811852049229a24336fe5eb6a439
- https://github.com/simonw/datasette-indieauth
- https://pypi.org/project/datasette-indieauth
