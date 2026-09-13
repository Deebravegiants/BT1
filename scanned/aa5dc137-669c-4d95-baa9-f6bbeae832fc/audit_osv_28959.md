# [M] CSP bypass in Hush Line

## Summary
Severity: Medium
Advisory: CVE-2024-38522
Aliases: GHSA-r85c-95x7-4h7q
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2024-06-28
Source: https://osv.dev/vulnerability/CVE-2024-38522
Type: osv

## Details
Hush Line is a free and open-source, anonymous-tip-line-as-a-service for organizations or individuals. The CSP policy applied on the `tips.hushline.app` website and bundled by default in this repository is trivial to bypass. This vulnerability has been patched in version 0.1.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38522.json
- https://github.com/scidsg/hushline/security/advisories/GHSA-r85c-95x7-4h7q
- https://nvd.nist.gov/vuln/detail/CVE-2024-38522
- https://github.com/scidsg/hushline/commit/2bbeae78a24ca2cd893f32a1812f5f6634cb21b6
