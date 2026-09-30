# [M] Vim has a Netbeans specialKeys Stack Buffer Overflow

## Summary
Severity: Medium
Advisory: CVE-2026-26269
Aliases: GHSA-9w5c-hwr9-hc68
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:L)
Published: 2026-02-13
Source: https://osv.dev/vulnerability/CVE-2026-26269
Type: osv

## Details
Vim is an open source, command line text editor. Prior to 9.1.2148, a stack buffer overflow vulnerability exists in Vim's NetBeans integration when processing the specialKeys command, affecting Vim builds that enable and use the NetBeans feature. The Stack buffer overflow exists in special_keys() (in src/netbeans.c). The while (*tok) loop writes two bytes per iteration into a 64-byte stack buffer (keybuf) with no bounds check. A malicious NetBeans server can overflow keybuf with a single specialKeys command. The issue has been fixed as of Vim patch v9.1.2148.

## References
- http://www.openwall.com/lists/oss-security/2026/02/13/2
- https://github.com/vim/vim/releases/tag/v9.1.2148
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26269.json
- https://github.com/vim/vim/security/advisories/GHSA-9w5c-hwr9-hc68
- https://nvd.nist.gov/vuln/detail/CVE-2026-26269
- https://github.com/vim/vim/commit/c5f312aad8e4179e437f81ad39a860cd0ef11970
