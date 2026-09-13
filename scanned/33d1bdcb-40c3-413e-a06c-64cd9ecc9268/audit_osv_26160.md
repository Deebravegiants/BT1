# [H] Path traversal via crafted cpio archives in Engrampa archivers

## Summary
Severity: High
Advisory: CVE-2023-52138
Aliases: GHSA-c98h-v39w-3r7v
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:H/A:N)
Published: 2024-02-05
Source: https://osv.dev/vulnerability/CVE-2023-52138
Type: osv

## Details
Engrampa is an archive manager for the MATE environment. Engrampa is found to be vulnerable to a Path Traversal vulnerability that can be leveraged to achieve full Remote Command Execution (RCE) on the target. While handling CPIO archives, the Engrampa Archive manager follows symlink, cpio by default will follow stored symlinks while extracting and the Archiver will not check the symlink location, which leads to arbitrary file writes to unintended locations. When the victim extracts the archive, the attacker can craft a malicious cpio or ISO archive to achieve RCE on the target system. This vulnerability was fixed in commit 63d5dfa.

## References
- https://lists.debian.org/debian-lts-announce/2024/02/msg00011.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4IOJ3QWXTZGCXFEHP72ELY22PZ4AX2CB/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52138.json
- https://github.com/mate-desktop/engrampa/security/advisories/GHSA-c98h-v39w-3r7v
- https://nvd.nist.gov/vuln/detail/CVE-2023-52138
- https://github.com/mate-desktop/engrampa/commit/63d5dfa9005c6b16d0f0ccd888cc859fca78f970
