# [C] Path traversal via unvalidated instance name in backup tarball restore enables root file write / RCE

## Summary
Severity: Critical
Advisory: CVE-2026-66898
Aliases: GHSA-m857-c7gc-c984
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-66898
Type: osv

## Details
A path traversal vulnerability in LXD allows an attacker to manipulate file system paths during backup import and restore operations. When importing or restoring a backup archive, LXD fails to validate instance and storage volume names contained within the archive metadata. An attacker can exploit this flaw by supplying a crafted backup archive with malicious instance or volume names containing path traversal sequences, potentially allowing file access or overwriting outside the designated restore directory.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66898.json
- https://github.com/canonical/lxd/security/advisories/GHSA-m857-c7gc-c984
- https://nvd.nist.gov/vuln/detail/CVE-2026-66898
- https://github.com/canonical/lxd
