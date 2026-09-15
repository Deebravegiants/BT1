# [C] Group-Office: Authenticated Remote Code Execution via PHP Insecure Deserialization in `AbstractSettingsCollection`

## Summary
Severity: Critical
Advisory: CVE-2026-34838
Aliases: GHSA-h22j-frrf-5vxq
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-04-02
Source: https://osv.dev/vulnerability/CVE-2026-34838
Type: osv

## Details
Group-Office is an enterprise customer relationship management and groupware tool. Prior to versions 6.8.156, 25.0.90, and 26.0.12, a vulnerability in the AbstractSettingsCollection model leads to insecure deserialization when these settings are loaded. By injecting a serialized FileCookieJar object into a setting string, an authenticated attacker can achieve Arbitrary File Write, leading directly to Remote Code Execution (RCE) on the server. This issue has been patched in versions 6.8.156, 25.0.90, and 26.0.12.

## References
- https://github.com/Intermesh/groupoffice/releases/tag/v25.0.90
- https://github.com/Intermesh/groupoffice/releases/tag/v26.0.12
- https://github.com/Intermesh/groupoffice/releases/tag/v6.8.156
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34838.json
- https://github.com/Intermesh/groupoffice/security/advisories/GHSA-h22j-frrf-5vxq
- https://nvd.nist.gov/vuln/detail/CVE-2026-34838
