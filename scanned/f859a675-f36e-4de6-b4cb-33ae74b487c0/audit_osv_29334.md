# [M] Vim double free in src/alloc.c:616

## Summary
Severity: Medium
Advisory: CVE-2024-41957
Aliases: GHSA-f9cr-gv85-hcr4
CVSS: 4.5 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2024-08-01
Source: https://osv.dev/vulnerability/CVE-2024-41957
Type: osv

## Details
Vim is an open source command line text editor. Vim < v9.1.0647 has double free in src/alloc.c:616. When closing a window, the corresponding tagstack data will be cleared and freed. However a bit later, the quickfix list belonging to that window will also be cleared and if that quickfix list points to the same tagstack data, Vim will try to free it again, resulting in a double-free/use-after-free access exception. Impact is low since the user must intentionally execute vim with several non-default flags,
but it may cause a crash of Vim. The issue has been fixed as of Vim patch v9.1.0647

## References
- http://seclists.org/fulldisclosure/2024/Sep/33
- http://www.openwall.com/lists/oss-security/2024/08/01/1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41957.json
- https://github.com/vim/vim/security/advisories/GHSA-f9cr-gv85-hcr4
- https://nvd.nist.gov/vuln/detail/CVE-2024-41957
- https://security.netapp.com/advisory/ntap-20241129-0007/
- https://github.com/vim/vim/commit/8a0bbe7b8aad6f8da28dee218c01bc8a0185a
