# [M] Vim vulnerable to potential data loss with zip.vim and special crafted zip files

## Summary
Severity: Medium
Advisory: CVE-2025-29768
Aliases: GHSA-693p-m996-3rmf
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N)
Published: 2025-03-13
Source: https://osv.dev/vulnerability/CVE-2025-29768
Type: osv

## Details
Vim, a text editor, is vulnerable to potential data loss with zip.vim and special crafted zip files in versions prior to 9.1.1198. The impact is medium because a user must be made to view such an archive with Vim and then press 'x' on such a strange filename. The issue has been fixed as of Vim patch v9.1.1198.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/29xxx/CVE-2025-29768.json
- https://github.com/vim/vim/security/advisories/GHSA-693p-m996-3rmf
- https://nvd.nist.gov/vuln/detail/CVE-2025-29768
- https://security.netapp.com/advisory/ntap-20250502-0001/
- https://github.com/vim/vim/commit/f209dcd3defb95bae21b2740910e6aa7bb940531
