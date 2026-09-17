# [H] Complete Bypass of CVE-2026-24884 Patch via Git-Delivered Symlink Poisoning in compressing

## Summary
Severity: High
Advisory: CVE-2026-40931
Aliases: GHSA-4c3q-x735-j3r5
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-40931
Type: osv

## Details
Compressing is a compressing and uncompressing lib for node. Prior to 2.1.1 and 1.10.5, the patch for CVE-2026-24884 relies on a purely logical string validation within the isPathWithinParent utility. This check verifies if a resolved path string starts with the destination directory string but fails to account for the actual filesystem state. By exploiting this "Logical vs. Physical" divergence, an attacker can bypass the security check using a Directory Poisoning technique (pre-existing symbolic links). This vulnerability is fixed in 2.1.1 and 1.10.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40931.json
- https://github.com/node-modules/compressing/security/advisories/GHSA-4c3q-x735-j3r5
- https://nvd.nist.gov/vuln/detail/CVE-2026-40931
