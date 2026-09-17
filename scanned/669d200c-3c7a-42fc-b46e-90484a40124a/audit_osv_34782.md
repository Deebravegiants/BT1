# [H] esm.sh CDN service has arbitrary file write via tarslip

## Summary
Severity: High
Advisory: CVE-2025-65025
Aliases: GHSA-h3mw-4f23-gwpw, GO-2025-4138
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N)
Published: 2025-11-19
Source: https://osv.dev/vulnerability/CVE-2025-65025
Type: osv

## Details
esm.sh is a nobuild content delivery network(CDN) for modern web development. Prior to version 136, the esm.sh CDN service is vulnerable to path traversal during NPM package tarball extraction. An attacker can craft a malicious NPM package containing specially crafted file paths (e.g., package/../../tmp/evil.js). When esm.sh downloads and extracts this package, files may be written to arbitrary locations on the server, escaping the intended extraction directory. This issue has been patched in version 136.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65025.json
- https://github.com/esm-dev/esm.sh/security/advisories/GHSA-h3mw-4f23-gwpw
- https://nvd.nist.gov/vuln/detail/CVE-2025-65025
- https://github.com/esm-dev/esm.sh/commit/9d77b88c320733ff6689d938d85d246a3af9af16
