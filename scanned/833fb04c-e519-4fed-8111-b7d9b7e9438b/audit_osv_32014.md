# [C] Arbitrary File Overwrite via HTTP POST in Pingvin Share

## Summary
Severity: Critical
Advisory: CVE-2025-22137
Aliases: GHSA-rjwx-p44f-mcrv
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-08
Source: https://osv.dev/vulnerability/CVE-2025-22137
Type: osv

## Details
Pingvin Share is a self-hosted file sharing platform and an alternative for WeTransfer. This vulnerability allows an authenticated or unauthenticated (if anonymous shares are allowed) user to overwrite arbitrary files on the server, including sensitive system files, via HTTP POST requests. The issue has been patched in version 1.4.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22137.json
- https://github.com/stonith404/pingvin-share/security/advisories/GHSA-rjwx-p44f-mcrv
- https://nvd.nist.gov/vuln/detail/CVE-2025-22137
- https://github.com/stonith404/pingvin-share/commit/6cf5c66fe2eda1e0a525edf7440d047fe2f0e35b
- https://github.com/stonith404/pingvin-share/commit/c52ec7192080c402bd804e69be93dd88cc7c5c70
