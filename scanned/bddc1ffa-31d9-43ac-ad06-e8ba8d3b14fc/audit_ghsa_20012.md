# [M] ghinstallation returns app JWT in error responses

## Summary
Severity: Medium
Advisory: GHSA-h4q8-96p6-jcgr
CVE: CVE-2022-39304
CWE: CWE-209
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:H/I:N/A:L (CVSS_V3)
Published: 2022-12-19
Source: https://github.com/advisories/GHSA-h4q8-96p6-jcgr
Type: github-advisory

## Affected
- Go: `github.com/bradleyfalzon/ghinstallation` — affected >=0 <2.0.0

## Details
### Impact

In ghinstallation v1, when the request to refresh an installation token failed, the HTTP request and response would be returned for debugging.

https://github.com/bradleyfalzon/ghinstallation/blob/24e56b3fb7669f209134a01eff731d7e2ef72a5c/transport.go#L172-L174

The request contained the bearer JWT for the App, and was returned back to clients. This token is short lived (10 minute maximum).

### Patches

- This has already been patched in d24f14f8be70d94129d76026e8b0f4f9170c8c3e, and is available in releases >= v2.0.0.

### References
_Are there any links users can visit to find out more?_

- See https://docs.github.com/en/developers/apps/building-github-apps/authenticating-with-github-apps#authenticating-as-an-installation for the App installation flow.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [ghinstallation](https://github.com/bradleyfalzon/ghinstallation)

## References
- https://github.com/bradleyfalzon/ghinstallation/security/advisories/GHSA-h4q8-96p6-jcgr
- https://nvd.nist.gov/vuln/detail/CVE-2022-39304
- https://github.com/bradleyfalzon/ghinstallation/commit/d24f14f8be70d94129d76026e8b0f4f9170c8c3e
- https://docs.github.com/en/developers/apps/building-github-apps/authenticating-with-github-apps#authenticating-as-an-installation
- https://github.com/bradleyfalzon/ghinstallation
- https://github.com/bradleyfalzon/ghinstallation/blob/24e56b3fb7669f209134a01eff731d7e2ef72a5c/transport.go#L172-L174
- https://pkg.go.dev/vuln/GO-2022-1178
- https://securitylab.github.com/advisories/GHSL-2022-061_ghinstallation
