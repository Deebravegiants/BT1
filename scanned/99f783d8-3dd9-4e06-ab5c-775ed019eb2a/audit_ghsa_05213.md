# [M] CoreWCF: SAML token replay protection is inoperative

## Summary
Severity: Medium
Advisory: GHSA-9jr3-rj99-8jq3
CVE: CVE-2026-54779
CWE: CWE-294, CWE-613
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-9jr3-rj99-8jq3
Type: github-advisory

## Affected
- NuGet: `CoreWCF.Primitives` — affected >=0 <1.8.1
- NuGet: `CoreWCF.Primitives` — affected >=1.9.0 <1.9.1

## Details
### Impact
When enabling DetectReplayedTokens, a token can be replayed and will be detected despite it being reused.

### Patches
Fixed in CoreWCF v1.8.1 and v1.9.1

### Workarounds
Provide your own implementation of `ITokenReplayCache` with the correct behavior.

## References
- https://github.com/CoreWCF/CoreWCF/security/advisories/GHSA-9jr3-rj99-8jq3
- https://github.com/CoreWCF/CoreWCF
