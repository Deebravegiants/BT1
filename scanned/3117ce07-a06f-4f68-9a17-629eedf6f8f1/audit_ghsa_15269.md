# [C] GoAuthentik vulnerable to Insufficient Authorization for several API endpoints

## Summary
Severity: Critical
Advisory: GHSA-qxqc-27pr-wgc8
CVE: CVE-2024-42490
CWE: CWE-285, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:N/A:H (CVSS_V3)
Published: 2024-08-22
Source: https://github.com/advisories/GHSA-qxqc-27pr-wgc8
Type: github-advisory

## Affected
- Go: `goauthentik.io` — affected >=2024.6.0-rc1 <2024.6.4
- Go: `goauthentik.io` — affected >=0 <2024.4.4

## Details
### Summary

Several API endpoints can be accessed by users without correct authentication/authorization.

The main API endpoints affected by this:

-   `/api/v3/crypto/certificatekeypairs/<uuid>/view_certificate/`
-   `/api/v3/crypto/certificatekeypairs/<uuid>/view_private_key/`
-   `/api/v3/.../used_by/`

Note that all of the affected API endpoints require the knowledge of the ID of an object, which especially for certificates is not accessible to an unprivileged user. Additionally the IDs for most objects are UUIDv4, meaning they are not easily guessable/enumerable.

### Patches

authentik 2024.4.4, 2024.6.4 and 2024.8.0 fix this issue.

### Workarounds

Access to the API endpoints can be blocked at a Reverse-proxy/Load balancer level to prevent this issue from being exploited.

### For more information

If you have any questions or comments about this advisory:

-   Email us at [security@goauthentik.io](mailto:security@goauthentik.io)

## References
- https://github.com/goauthentik/authentik/security/advisories/GHSA-qxqc-27pr-wgc8
- https://nvd.nist.gov/vuln/detail/CVE-2024-42490
- https://github.com/goauthentik/authentik/commit/19318d4c00bb02c4ec3c4f8f15ac2e1dbe8d846c
- https://github.com/goauthentik/authentik/commit/359b343f51524342a5ca03828e7c975a1d654b11
- https://github.com/goauthentik/authentik
