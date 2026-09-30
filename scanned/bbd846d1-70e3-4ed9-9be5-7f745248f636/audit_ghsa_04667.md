# [H] CoreWCF: XML Signature Wrapping in WS-Security endorsing/supporting signature verification allows replay of captured signed messages

## Summary
Severity: High
Advisory: GHSA-gqv6-pwcg-87r8
CVE: CVE-2026-54783
CWE: CWE-294, CWE-345, CWE-347
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-gqv6-pwcg-87r8
Type: github-advisory

## Affected
- NuGet: `CoreWCF.Primitives` — affected >=0 <1.8.1
- NuGet: `CoreWCF.Primitives` — affected >=1.9.0 <1.9.1

## Details
### Impact
The attacker, with one captured signed SOAP envelope from a victim and no other privileges, can invoke arbitrary operations on the service as the victim principal for the lifetime of the captured signing key. There is no rate limit on replays. The DetectReplays setting on transport-security bindings does not mitigate the issue because the attack does not reuse the original timestamp — the fresh timestamp in the wsse:Security header is what the replay-detection logic inspects.

### Patches
Fixed in CoreWCF v1.8.1 and v1.9.1

### Workarounds
Ensure communication is protected by SSL/TLS to prevent capturing of signed SOAP envelope.

## References
- https://github.com/CoreWCF/CoreWCF/security/advisories/GHSA-gqv6-pwcg-87r8
- https://github.com/CoreWCF/CoreWCF
