# [C] Prebid-universal-creative latest on npm briefly compromised

## Summary
Severity: Critical
Advisory: GHSA-m662-56rj-8fmm
CVE: CVE-2025-59039
CWE: CWE-506
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-11
Source: https://github.com/advisories/GHSA-m662-56rj-8fmm
Type: github-advisory

## Affected
- npm: `prebid-universal-creative` — affected 1.17.3

## Details
### Impact
Npm users of PUC 1.17.3 or PUC latest were briefly affected by crypto-related malware detailed in the blog post below. This includes the extremely popular jsdelivr hosting of this file. 

### Patches
We unpublished the version on npm.

### Workarounds
This has already been unpublished. See Prebid.js 9 release notes for suggestions on moving off the deprecated workflow of using the PUC or pointing to a dynamic version of it. PUC users pointing to latest should transition to 1.17.2 ASAP to avoid similar attacks in the future.

### References
https://www.sonatype.com/blog/npm-chalk-and-debug-packages-hit-in-software-supply-chain-attack

## References
- https://github.com/prebid/prebid-universal-creative/security/advisories/GHSA-m662-56rj-8fmm
- https://nvd.nist.gov/vuln/detail/CVE-2025-59039
- https://github.com/prebid/prebid-universal-creative
- https://www.sonatype.com/blog/npm-chalk-and-debug-packages-hit-in-software-supply-chain-attack
