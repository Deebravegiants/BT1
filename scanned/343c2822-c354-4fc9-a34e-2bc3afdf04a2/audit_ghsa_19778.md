# [M] Parse Server has an OAuth login vulnerability

## Summary
Severity: Medium
Advisory: GHSA-837q-jhwx-cmpv
CVE: CVE-2025-30168
CWE: CWE-287
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2025-03-21
Source: https://github.com/advisories/GHSA-837q-jhwx-cmpv
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=0 <7.5.2
- npm: `parse-server` — affected >=8.0.0 <8.0.2

## Details
### Impact

The 3rd party authentication handling of Parse Server allows the authentication credentials of some specific authentication providers to be used across multiple Parse Server apps. For example, if a user signed up using the same authentication provider in two unrelated Parse Server apps, the credentials stored by one app can be used to authenticate the same user in the other app. Note that this only affects Parse Server apps that specifically use an affected 3rd party authentication provider for user authentication, for example by setting the Parse Server option `auth` to configure a Parse Server authentication adapter. See the [3rd party authentication docs](https://docs.parseplatform.org/parse-server/guide/#oauth-and-3rd-party-authentication) for more information on which authentication providers are affected.

### Patches

The fix of this vulnerability requires to upgrade Parse Server to a version that includes the bug fix, as well as upgrade the client app to send a secure payload, which is different from the previous insecure payload. To accommodate a gradual rollout of the client app update, affected Parse Server authentication adapters now offer an `enableInsecureAuth` option to accept both insecure and secure payloads from clients apps. See the [3rd party authentication docs](https://docs.parseplatform.org/parse-server/guide/#oauth-and-3rd-party-authentication) for how to migrate from insecure to secure authentication.

### Workarounds

None.

### References
- GitHub security advisory: https://github.com/parse-community/parse-server/security/advisories/GHSA-837q-jhwx-cmpv
- Parse Server documentation for 3rd party authentication providers: https://docs.parseplatform.org/parse-server/guide/#oauth-and-3rd-party-authentication
- Bug fix in Parse Server 7: https://github.com/parse-community/parse-server/pull/9668
- Bug fix in Parse Server 8: https://github.com/parse-community/parse-server/pull/9667

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-837q-jhwx-cmpv
- https://nvd.nist.gov/vuln/detail/CVE-2025-30168
- https://github.com/parse-community/parse-server/pull/9667
- https://github.com/parse-community/parse-server/pull/9668
- https://github.com/parse-community/parse-server/commit/2ff9c71030bce3aada0a00fbceedeb7ae2c8a41e
- https://github.com/parse-community/parse-server/commit/5ef0440c8e763854e62341acaeb6dc4ade3ba82f
- https://docs.parseplatform.org/parse-server/guide/#oauth-and-3rd-party-authentication
- https://github.com/parse-community/parse-server
