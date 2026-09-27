# [M] NanoClaw < 2.1.17 - Arbitrary File Read via Symlink Following in forwardAttachedFiles

## Summary
Severity: Medium
Advisory: CVE-2026-56692
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-23
Source: https://osv.dev/vulnerability/CVE-2026-56692
Type: osv

## Details
NanoClaw before 2.1.17 contains a symlink following vulnerability in forwardAttachedFiles that allows container-controlled agents to exfiltrate host-readable files. The host validates attachment filenames using only isSafeAttachmentName before copying with fs.copyFileSync, which follows symlinks without containment checks, allowing malicious agents to disclose arbitrary host files.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56692.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-56692
- https://www.vulncheck.com/advisories/nanoclaw-arbitrary-file-read-via-symlink-following-in-forwardattachedfiles
- https://github.com/nanocoai/nanoclaw/pull/2468
- https://github.com/nanocoai/nanoclaw/commit/28032bc0eca76c91fb3d8be0013e8bcaf2f5aeae
- https://github.com/nanocoai/nanoclaw
