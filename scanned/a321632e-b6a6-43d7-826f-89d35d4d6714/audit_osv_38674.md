# [M] Vim: Command injection via backtick expansion in tag filenames

## Summary
Severity: Medium
Advisory: CVE-2026-41411
Aliases: GHSA-cwgx-gcj7-6qh8
CVSS: 6.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:H/A:L)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-41411
Type: osv

## Details
Vim is an open source, command line text editor. Prior to 9.2.0357, A command injection vulnerability exists in Vim's tag file processing. When resolving a tag, the filename field from the tags file is passed through wildcard expansion to resolve environment variables and wildcards. If the filename field contains backtick syntax (e.g., `command`), Vim executes the embedded command via the system shell with the full privileges of the running user.

## References
- https://github.com/vim/vim/releases/tag/v9.2.0357
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41411.json
- https://github.com/vim/vim/security/advisories/GHSA-cwgx-gcj7-6qh8
- https://nvd.nist.gov/vuln/detail/CVE-2026-41411
- https://github.com/vim/vim/commit/c78194e41d5a0b05b0ddf383b6679b1503f977fb
