# [M] SunshineService Has Unquoted Service Path That Allows Local SYSTEM Code Execution

## Summary
Severity: Medium
Advisory: CVE-2025-54081
Aliases: GHSA-6p7j-5v8v-w45h
CVSS: 6.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-09-23
Source: https://osv.dev/vulnerability/CVE-2025-54081
Type: osv

## Details
Sunshine is a self-hosted game stream host for Moonlight. Prior to version 2025.923.33222, the Windows service SunshineService is installed with an unquoted executable path. If Sunshine is installed in a directory whose name includes a space, the Service Control Manager (SCM) interprets the path incrementally and may execute a malicious binary placed earlier in the search string. This issue has been patched in version 2025.923.33222.

## References
- https://github.com/LizardByte/Sunshine/releases/tag/v2025.923.33222
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54081.json
- https://github.com/LizardByte/Sunshine/security/advisories/GHSA-6p7j-5v8v-w45h
- https://nvd.nist.gov/vuln/detail/CVE-2025-54081
- https://github.com/LizardByte/Sunshine/commit/f22b00d6981f756d3531fba0028723d4a5065824
