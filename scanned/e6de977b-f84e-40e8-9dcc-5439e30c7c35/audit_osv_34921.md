# [H] MaxKB has a Python sandbox LD_PRELOAD bypass

## Summary
Severity: High
Advisory: CVE-2025-66446
Aliases: GHSA-5xx2-3q9w-jpgf
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-11
Source: https://osv.dev/vulnerability/CVE-2025-66446
Type: osv

## Details
MaxKB is an open-source AI assistant for enterprise. Versions 2.3.1 and below have improper file permissions which allow attackers to overwrite the built-in dynamic linker and other critical files, potentially resulting in privilege escalation. This issue is fixed in version 2.4.0.

## References
- https://github.com/1Panel-dev/MaxKB/releases/tag/v2.4.0
- https://github.com/1Panel-dev/MaxKB/security/advisories/GHSA-5xx2-3q9w-jpgf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66446.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-66446
