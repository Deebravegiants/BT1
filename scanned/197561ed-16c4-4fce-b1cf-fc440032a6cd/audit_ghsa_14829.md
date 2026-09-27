# [M] Arbitrary file read via Playwright's screenshot feature exploiting file wrapper

## Summary
Severity: Medium
Advisory: GHSA-665w-mwrr-77q3
CVE: CVE-2024-37169
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-06-05
Source: https://github.com/advisories/GHSA-665w-mwrr-77q3
Type: github-advisory

## Affected
- npm: `@jmondi/url-to-png` — affected >=0 <2.0.3

## Details
### Impact

All users of url-to-png. Please see https://github.com/jasonraimondi/url-to-png/issues/47

### Patches

[v2.0.3](https://github.com/jasonraimondi/url-to-png/releases/tag/v2.0.3) requires input url to be of protocol `http` or `https` 

### Workarounds

Requires upgrade.

### References

- https://github.com/jasonraimondi/url-to-png/issues/47
- https://github.com/user-attachments/files/15536336/Arbitrary.File.Read.via.Playwright.s.Screenshot.Feature.Exploiting.File.Wrapper.pdf

## References
- https://github.com/jasonraimondi/url-to-png/security/advisories/GHSA-665w-mwrr-77q3
- https://nvd.nist.gov/vuln/detail/CVE-2024-37169
- https://github.com/jasonraimondi/url-to-png/issues/47
- https://github.com/jasonraimondi/url-to-png/commit/9336020c5e603323f5cf4a2ac3bb9a7735cf61f7
- https://github.com/jasonraimondi/url-to-png
- https://github.com/jasonraimondi/url-to-png/releases/tag/v2.0.3
- https://github.com/user-attachments/files/15536336/Arbitrary.File.Read.via.Playwright.s.Screenshot.Feature.Exploiting.File.Wrapper.pdf
