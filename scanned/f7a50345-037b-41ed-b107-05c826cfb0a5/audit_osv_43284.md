# [M] RustDesk Path Traversal via macOS Clipboard File-Paste

## Summary
Severity: Medium
Advisory: CVE-2026-73102
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-73102
Type: osv

## Details
RustDesk versions 1.3.9 through 1.4.9 contain a path traversal vulnerability in the macOS clipboard file-paste code path. The application accepts peer-supplied file descriptor names and joins them to the selected target directory without requiring normalized relative paths. A remote peer in an active clipboard file-paste session can use parent-directory components or absolute paths to write files outside the intended target directory at locations writable by the RustDesk process. Commit 6f1eb16 fixes the issue by validating descriptor names and safely joining paths.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73102.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-73102
- https://www.vulncheck.com/advisories/rustdesk-path-traversal-via-macos-clipboard-file-paste
- https://github.com/rustdesk/rustdesk/commit/6f1eb164d616e0e2bfbcf8c6b7c8083b09d7ed06
- https://github.com/rustdesk/rustdesk/pull/15693
- https://github.com/rustdesk/rustdesk
