# [H] SSHFS: Improper Neutralization of Argument Delimiters in a Command ('Argument Injection')

## Summary
Severity: High
Advisory: CVE-2026-48711
Aliases: GHSA-mm85-q63v-4476
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-48711
Type: osv

## Details
SSHFS is a network filesystem client for connecting to SSH servers. From version 1.4 until 3.7.6, SSHFS accepts a bracketed mount source such as [-oProxyCommand=CMD]:/path and find_base_path() removes the brackets, leaving a host value that begins with - and is passed directly to ssh as a command-line argument. When a caller also supplies a path-valued sftp_server, ssh treats the normalized host as an option and the server path as its destination, causing an injected ProxyCommand to execute locally before any connection or authentication succeeds. The attack requires a caller or wrapper that passes an attacker-controlled mount source to SSHFS with the required sftp_server configuration and results in arbitrary command execution as the user running SSHFS. This issue is fixed in version 3.7.6.

## References
- https://github.com/libfuse/sshfs/releases/tag/sshfs-3.7.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48711.json
- https://github.com/libfuse/sshfs/security/advisories/GHSA-mm85-q63v-4476
- https://nvd.nist.gov/vuln/detail/CVE-2026-48711
- https://github.com/libfuse/sshfs/commit/29bb565ea6405e2dd5a0ea65fe64da117e76055e
- https://github.com/libfuse/sshfs/pull/362
