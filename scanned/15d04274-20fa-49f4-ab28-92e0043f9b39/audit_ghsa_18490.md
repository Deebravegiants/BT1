# [H] files-bucket-server vulnerable to Directory Traversal

## Summary
Severity: High
Advisory: GHSA-3r3j-4vrw-884j
CVE: CVE-2025-8021
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-07-23
Source: https://github.com/advisories/GHSA-3r3j-4vrw-884j
Type: github-advisory

## Affected
- npm: `files-bucket-server` — affected >=0

## Details
All versions of the package files-bucket-server are vulnerable to Directory Traversal, where an attacker can traverse the file system and access files outside of the intended directory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-8021
- https://gist.github.com/lirantal/1f833a7d445e8cfbdcb3e75022954b35#path-traversal-vulnerability-in-files-bucket-server
- https://github.com/dsilva2401/files-bucket-server
- https://security.snyk.io/vuln/SNYK-JS-FILESBUCKETSERVER-9510944
