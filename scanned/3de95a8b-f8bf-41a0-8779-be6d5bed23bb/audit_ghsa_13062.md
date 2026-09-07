# [M] @excalidraw/excalidraw Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-v7v8-gjv7-ffmr
CVE: CVE-2023-26140
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-08-16
Source: https://github.com/advisories/GHSA-v7v8-gjv7-ffmr
Type: github-advisory

## Affected
- npm: `@excalidraw/excalidraw` — affected >=0 <0.15.3

## Details
### Impact

XSS vulnerability due to improperly sanitizing URLs of links that can be attached on canvas elements. This affects users of the npm package `@excalidraw/excalidraw` provided it was deployed in environments where untrusted user input in drawings that are then shared with third parties is a concern. If you only hosted the editor in trusted environments, or sharing didn't take place, the impact is minimized.

### Patches

Patch is available on version 0.15.3 and up (stable), or latest `@excalidraw/excalidraw@next` (unstable releases).

### Workarounds

No workaround without upgrading unless deployed in environments without untrusted user input.

### References

https://security.snyk.io/vuln/SNYK-JS-EXCALIDRAWEXCALIDRAW-5841658
https://github.com/excalidraw/excalidraw/pull/6728

## References
- https://github.com/excalidraw/excalidraw/security/advisories/GHSA-v7v8-gjv7-ffmr
- https://nvd.nist.gov/vuln/detail/CVE-2023-26140
- https://github.com/excalidraw/excalidraw/pull/6728
- https://github.com/excalidraw/excalidraw/commit/b33fa6d6f64d27adc3a47b25c0aa55711740d0af
- https://github.com/excalidraw/excalidraw
- https://security.snyk.io/vuln/SNYK-JS-EXCALIDRAWEXCALIDRAW-5841658
