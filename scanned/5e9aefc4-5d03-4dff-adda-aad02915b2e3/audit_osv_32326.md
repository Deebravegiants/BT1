# [M] Element X Android vulnerable to loading malicious web pages via received intent

## Summary
Severity: Medium
Advisory: CVE-2025-27599
Aliases: GHSA-m5px-pwq3-4p5m
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-04-18
Source: https://osv.dev/vulnerability/CVE-2025-27599
Type: osv

## Details
Element X Android is a Matrix Android Client provided by element.io. Prior to version 25.04.2, a crafted hyperlink on a webpage, or a locally installed malicious app, can force Element X up to version 25.04.1 to load a webpage with similar permissions to Element Call and automatically grant it temporary access to microphone and camera. This issue has been patched in version 25.04.2.

## References
- https://github.com/element-hq/element-x-android/releases/tag/v25.04.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27599.json
- https://github.com/element-hq/element-x-android/security/advisories/GHSA-m5px-pwq3-4p5m
- https://nvd.nist.gov/vuln/detail/CVE-2025-27599
- https://github.com/element-hq/element-x-android/commit/dc058544d7e693c04298191c1aadd5b39c9be52e
