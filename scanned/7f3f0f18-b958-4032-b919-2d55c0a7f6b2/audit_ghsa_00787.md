# [C] Server secret was included in static assets and served to clients

## Summary
Severity: Critical
Advisory: GHSA-r587-7jh2-4qr3
Ecosystem: npm
Published: 2020-08-26
Source: https://github.com/advisories/GHSA-r587-7jh2-4qr3
Type: github-advisory

## Affected
- npm: `flood` — affected >=2.0.0 <3.0.0

## Details
### Impact
Server JWT signing secret was included in static assets and served to clients.

This ALLOWS Flood's builtin authentication to be bypassed. Given Flood is granted access to rTorrent's SCGI interface (which is unprotected and ALLOWS arbitrary code execution) and usually wide-ranging privileges to files, along with Flood's lack of security controls against authenticated users, the severity of this vulnerability is **CRITICAL**. 

### Background
Commit 8d11640b imported `config.js` to client (frontend) components to get `disableUsersAndAuth` configuration variable. Subsequently contents of `config.js` are compiled into static assets and served to users. Unfortunately `config.js` also includes `secret`.

Intruders can use `secret` to sign authentication tokens themselves to bypass builtin access control of Flood.

### Patches
Commit 042cb4ce removed imports of `config.js` from client (frontend) components. Additionally an eslint rule was added to prevent config.js from being imported to client (frontend) components.

Commit 103f53c8 provided a general mitigation to this kind of problem by searching static assets to ensure `secret` is not included before starting server (backend). 

### Workarounds
Users shall upgrade if they use Flood's builtin authentication system.

While maintainers will do their best to support it, Flood cannot guarantee its in-house access control system can stand against determined attackers in high-stake environments. 

> Use `HTTP Basic Auth` or other battle-hardened authentication methods instead of Flood's in-house one. You can use `disableUsersAndAuth` to avoid duplicate authentication.

Users are advised to check out the [wiki](https://github.com/jesec/flood/wiki) for more information on security precautions.

### References
[Wiki - Security precautions](https://github.com/jesec/flood/wiki/Security-precautions)

[Introduction to JSON Web Tokens](https://jwt.io/introduction/)

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [issue tracker](https://github.com/jesec/flood/issues)
* Email us at [jc@linux.com](mailto:jc@linux.com)

## References
- https://github.com/jesec/flood/security/advisories/GHSA-r587-7jh2-4qr3
- https://github.com/jesec/flood/commit/103f53c8d2963584e41bcf46ccc6fe0fabf179ca
- https://github.com/jesec/flood/commit/d137107ac908526d43966607149fbaf00cfcedf0
- https://github.com/jesec/flood
