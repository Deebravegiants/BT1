# [H] Switcher Client contains Regular Expression Denial of Service (ReDoS)

## Summary
Severity: High
Advisory: GHSA-wqxw-8h5g-hq56
CVE: CVE-2023-23925
CWE: CWE-1333, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-02-02
Source: https://github.com/advisories/GHSA-wqxw-8h5g-hq56
Type: github-advisory

## Affected
- npm: `switcher-client` — affected >=0 <3.1.4

## Details
### Impact
Unsanitized input flows into Strategy match operation (EXIST), where it is used to build a regular expression. This may result in a Regular expression Denial of Service attack (reDOS).

### Patches
Patched in 3.1.4

### Workarounds
Avoid using Strategy settings that use REGEX in conjunction with EXIST and NOT_EXIST operations.

## References
- https://github.com/switcherapi/switcher-client-master/security/advisories/GHSA-wqxw-8h5g-hq56
- https://nvd.nist.gov/vuln/detail/CVE-2023-23925
- https://github.com/switcherapi/switcher-client-master/commit/374752563d6ce9353ee592b40c809c8136f24930
- https://github.com/switcherapi/switcher-client-master
- https://github.com/switcherapi/switcher-client-master/releases/tag/v3.1.4
