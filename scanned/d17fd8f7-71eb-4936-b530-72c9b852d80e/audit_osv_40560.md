# [H] Termix: Tar option injection in file-manager archive creation allows command execution on managed SSH hosts

## Summary
Severity: High
Advisory: CVE-2026-53542
Aliases: GHSA-rwj6-6vh7-45pv
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-53542
Type: osv

## Details
Termix is a web-based server management platform with SSH terminal, tunneling, and file editing capabilities. Prior to 2.3.2, the archive creation endpoint in src/backend/ssh/file-manager.ts passes selected file basenames to tar without an end-of-options marker and without making the operands unambiguously relative. A user with access to an SSH file-manager session can select basenames beginning with GNU tar options such as --checkpoint=1 and --checkpoint-action=exec, causing tar, tar.gz, tar.bz2, or tar.xz creation to interpret those names as options. The resulting checkpoint action executes commands on the managed SSH host with the privileges of the connected SSH account, allowing file disclosure, modification, and service disruption. This issue is fixed in version 2.3.2.

## References
- https://github.com/Termix-SSH/Termix/releases/tag/release-2.3.2-tag
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53542.json
- https://github.com/Termix-SSH/Termix/security/advisories/GHSA-rwj6-6vh7-45pv
- https://nvd.nist.gov/vuln/detail/CVE-2026-53542
- https://github.com/Termix-SSH/Termix/commit/52f4e51ae03b5b8d2608e1383e2ccf79d290132b
- https://github.com/Termix-SSH/Termix/pull/874
