# [M] Http request which redirect to another hostname do not strip authorization header in @actions/http-client

## Summary
Severity: Medium
Advisory: GHSA-9w6v-m7wp-jwg4
CVE: CVE-2020-11021
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2020-04-29
Source: https://github.com/advisories/GHSA-9w6v-m7wp-jwg4
Type: github-advisory

## Affected
- npm: `@actions/http-client` — affected >=0 <1.0.8

## Details
### Impact
If consumers of the http-client:
  1. make an http request with an authorization header
  2. that request leads to a redirect (302) and
  3. the redirect url redirects to another domain or hostname 

The authorization header will get passed to the other domain.

Note that since this library is for actions, the GITHUB_TOKEN that is available in actions is generated and scoped per job with [these permissions](https://help.github.com/en/actions/configuring-and-managing-workflows/authenticating-with-the-github_token#permissions-for-the-github_token).

### Patches
The problem is fixed in 1.0.8 at [npm here](https://www.npmjs.com/package/@actions/http-client).  In 1.0.8, the authorization header is stripped before making the redirected request if the hostname is different.

### Workarounds
None.

### References
https://github.com/actions/http-client/pull/27

### For more information
If you have any questions or comments about this advisory:
* Open an issue in https://github.com/actions/http-client/issues

## References
- https://github.com/actions/http-client/security/advisories/GHSA-9w6v-m7wp-jwg4
- https://nvd.nist.gov/vuln/detail/CVE-2020-11021
- https://github.com/actions/http-client/pull/27
- https://github.com/actions/http-client/commit/f6aae3dda4f4c9dc0b49737b36007330f78fd53a
- https://github.com/actions/http-client
