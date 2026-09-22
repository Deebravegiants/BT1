# [C] Etherpad: JWT `admin` claim presence-only check lets non-admin OAuth users invoke every Etherpad HTTP API endpoint

## Summary
Severity: Critical
Advisory: CVE-2026-55089
Aliases: GHSA-qfmh-fph3-mw8q
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-55089
Type: osv

## Details
Etherpad is a real-time collaborative editor. From 2.1.0 until 3.1.0, Etherpad's src/node/handler/APIHandler.ts authorizes requests to /api/2/* in the authorization_code OAuth path by using requiredClaims with the admin claim. This check requires only that the claim exists, while src/node/security/OAuth2Provider.ts issues admin: false for configured non-admin users. A non-admin user with a valid signed token can therefore invoke administrative functions including setHTML, setText, appendText, deletePad, copyPad, movePad, restoreRevision, anonymizeAuthor, listAllPads, and listAuthorsOfPad, allowing disclosure, modification, or deletion of pads across the instance. This issue is fixed in version 3.1.0.

## References
- https://github.com/ether/etherpad/releases/tag/v3.1.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55089.json
- https://github.com/ether/etherpad/security/advisories/GHSA-qfmh-fph3-mw8q
- https://nvd.nist.gov/vuln/detail/CVE-2026-55089
- https://github.com/ether/etherpad/commit/8c6104c5d5daf41f0d454acc04d42dffa0e0d996
- https://github.com/ether/etherpad/pull/7784
