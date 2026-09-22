# [C] Rocket.Chat: Pre-Auth NoSQL Injection in CAS Login Handler leading to Arbitrary CAS/SAML User Session Hijack

## Summary
Severity: Critical
Advisory: CVE-2026-45688
Aliases: GHSA-rr54-jf4h-6cj9
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-45688
Type: osv

## Details
Rocket.Chat is an open-source, secure, fully customizable communications platform. Prior to 8.5.0, 8.4.1, 8.3.3, 8.2.3, 8.1.4, 8.0.5, 7.13.7, and 7.10.11, Rocket.Chat's CAS login handler forwards the client-supplied options.cas.credentialToken value straight into a MongoDB findOne({_id: ...}) query without any runtime type check. TypeScript's string parameter annotation is erased at runtime, so an unauthenticated attacker can substitute a MongoDB query operator ({"$gt": ""}, {"$ne": null}, etc.) for what the server expects to be an opaque ticket string. The injected operator matches the first unexpired document in the credential_tokens collection, bypassing the CAS ticket check entirely. When any legitimate CAS or SAML SSO login is in flight, the attacker's next DDP login call matches the same credential-token row via the NoSQL operator and is issued a full Meteor auth token (userId + token) bound to the victim. The token is immediately usable against the complete REST and DDP surface as that user. If the victim is an administrator, this escalates to full instance compromise via Apps-Engine app install. This vulnerability is fixed in 8.5.0, 8.4.1, 8.3.3, 8.2.3, 8.1.4, 8.0.5, 7.13.7, and 7.10.11.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45688.json
- https://github.com/RocketChat/Rocket.Chat/security/advisories/GHSA-rr54-jf4h-6cj9
- https://nvd.nist.gov/vuln/detail/CVE-2026-45688
