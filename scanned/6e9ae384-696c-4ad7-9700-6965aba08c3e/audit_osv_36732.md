# [H] OpenSlides has incorrect access control vulnerability in authentication service

## Summary
Severity: High
Advisory: CVE-2026-25519
Aliases: GHSA-vv4h-8wfc-pf8c
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-04
Source: https://osv.dev/vulnerability/CVE-2026-25519
Type: osv

## Details
OpenSlides is a free, web based presentation and assembly system for managing and projecting agenda, motions and elections of an assembly. Prior to version 4.2.29, OpenSlides supports local logins with username and password or an optionally configurable single sign on with SAML via an external IDP. For users synced to OpenSlides via an external IDP, there is an incorrect access control regarding the local login of these users. Users can successfully login using the local login form and the OpenSlides username of a SAML user and a trivial password. This password is valid for all SAML users. This issue has been patched in version 4.2.29.

## References
- https://github.com/OpenSlides/OpenSlides/releases/tag/4.2.29
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25519.json
- https://github.com/OpenSlides/OpenSlides/security/advisories/GHSA-vv4h-8wfc-pf8c
- https://nvd.nist.gov/vuln/detail/CVE-2026-25519
- https://github.com/OpenSlides/openslides-auth-service/commit/70c1aa9f5e1db59ec120ecce98d1c1169350a4ee
- https://github.com/OpenSlides/openslides-auth-service/pull/889
