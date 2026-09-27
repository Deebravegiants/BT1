# [C] Vim: Vimscript Code Injection in netrw NetrwLocalRmFile() via crafted filename

## Summary
Severity: Critical
Advisory: CVE-2026-55895
Aliases: GHSA-vhh8-v6wx-hjjh
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-55895
Type: osv

## Details
Vim is an open source, command line text editor. Prior to 9.2.0663, a Vimscript code injection vulnerability exists in s:NetrwLocalRmFile() in the netrw plugin (runtime/pack/dist/opt/netrw/autoload/netrw.vim) when deleting a local file from the browser. A filename derived from the buffer's directory listing is interpolated into an Ex command line passed to :execute with only the backslash character escaped, allowing a crafted filename containing a bar (|) to terminate the intended command and execute arbitrary Vimscript, including shell commands via :call system() and :!.  This vulnerability is fixed in 9.2.0663.

## References
- https://github.com/vim/vim/releases/tag/v9.2.0663
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55895.json
- https://github.com/vim/vim/security/advisories/GHSA-vhh8-v6wx-hjjh
- https://nvd.nist.gov/vuln/detail/CVE-2026-55895
- https://github.com/vim/vim/commit/55bc757a5d436e59d50fe43f7cda94b118f86cb2
