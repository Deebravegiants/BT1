# [C] OpenDJ SASL PLAIN authzid bypassing the proxy ACI scope check

## Summary
Severity: Critical
Advisory: GHSA-p279-2cqp-84jg
CVE: CVE-2026-73644
CWE: CWE-285, CWE-639
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-p279-2cqp-84jg
Type: github-advisory

## Affected
- Maven: `org.openidentityplatform.opendj:opendj-server-legacy` — affected >=0 <5.1.2

## Details
### Summary
When a SASL PLAIN bind supplies an authorization identity (authzid) that resolves to a **different** user, PlainSASLMechanismHandler verified only the PROXIED_AUTH privilege and never evaluated the "proxy" access-control right (the mayProxy ACI scope check). As a result, any account holding the proxied-auth privilege could assume **any resolvable non-root identity** without being granted a proxy ACI for that target.

This diverges from every other proxy path in OpenDJ — the proxied-authorization controls (RFC 4370) and the DIGEST-MD5 / GSSAPI authzid handlers all require **both** the privilege **and** the mayProxy scope grant.

### Impact
Privilege escalation / authorization bypass: a holder of proxied-auth can act as arbitrary directory users beyond the scope intended by the deployment's proxy ACIs, defeating the ACI-based restriction on *which* identities may be impersonated. Root/Directory Manager is not assumable this way.

### Fix
Enforce the mayProxy scope check on the SASL PLAIN authzid path (both dn: and u:/bare forms), sharing one hasProxyAccess helper with the DIGEST-MD5/GSSAPI path. Denial returns INVALID_CREDENTIALS (49) **before** password verification — matching DIGEST-MD5/GSSAPI — so an unauthenticated client cannot distinguish a missing privilege from a missing ACI grant.

### Workaround
Restrict or revoke the proxied-auth privilege until upgraded.

## References
- https://github.com/OpenIdentityPlatform/OpenDJ/security/advisories/GHSA-p279-2cqp-84jg
- https://github.com/OpenIdentityPlatform/OpenDJ/commit/5c326850f1ab945cfca7ac9c5aaf77d1052c6bed
- https://github.com/OpenIdentityPlatform/OpenDJ
- https://github.com/OpenIdentityPlatform/OpenDJ/releases/tag/5.1.2
