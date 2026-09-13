# [H] Bubblewrap: bubblewrap: symlink traversal via /oldroot allows writing files outside sandbox during setup

## Summary
Severity: High
Advisory: CVE-2026-87766
Aliases: GHSA-pxhw-h44j-8pfx
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-87766
Type: osv

## Details
A flaw was found in bubblewrap. During sandbox setup, creating files or directories under the new root can follow a parent symlink onto the host via /oldroot, writing attacker-chosen paths outside the sandbox as the launching user. This happens before the sandboxed process starts. This issue is GHSA-pxhw-h44j-8pfx. It is fixed in bubblewrap 0.12.0.

## References
- http://www.openwall.com/lists/oss-security/2026/09/09/3
- https://access.redhat.com/downloads/content/package-browser/
- https://bugs.debian.org/1145655
- https://github.com/containers/bubblewrap/releases/tag/v0.12.0
- https://www.openwall.com/lists/oss-security/2026/08/27/7
- https://access.redhat.com/security/cve/CVE-2026-87766
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/87xxx/CVE-2026-87766.json
- https://github.com/containers/bubblewrap/security/advisories/GHSA-pxhw-h44j-8pfx
- https://nvd.nist.gov/vuln/detail/CVE-2026-87766
- https://bugzilla.redhat.com/show_bug.cgi?id=2530542
