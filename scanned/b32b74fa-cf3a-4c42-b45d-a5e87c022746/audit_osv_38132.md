# [H] OneUptime SSO: Multi-Assertion Identity Injection via Decoupled Signature Verification

## Summary
Severity: High
Advisory: CVE-2026-34840
Aliases: GHSA-5w5c-766x-265g
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-04-02
Source: https://osv.dev/vulnerability/CVE-2026-34840
Type: osv

## Details
OneUptime is an open-source monitoring and observability platform. Prior to version 10.0.42, OneUptime's SAML SSO implementation (App/FeatureSet/Identity/Utils/SSO.ts) has decoupled signature verification and identity extraction. isSignatureValid() verifies the first <Signature> element in the XML DOM using xml-crypto, while getEmail() always reads from assertion[0] via xml2js. An attacker can prepend an unsigned assertion containing an arbitrary identity before a legitimately signed assertion, resulting in authentication bypass. This issue has been patched in version 10.0.42.

## References
- https://github.com/OneUptime/oneuptime/releases/tag/10.0.42
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34840.json
- https://github.com/OneUptime/oneuptime/security/advisories/GHSA-5w5c-766x-265g
- https://nvd.nist.gov/vuln/detail/CVE-2026-34840
- https://github.com/OneUptime/oneuptime/commit/2fd7ede52f60444710628d6c1b34dee2ef9e57d1
