# [M] Vim double-free vulnerability during Vim9 script import operations

## Summary
Severity: Medium
Advisory: CVE-2025-55158
Aliases: GHSA-5fg8-wvx3-583x
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2025-08-11
Source: https://osv.dev/vulnerability/CVE-2025-55158
Type: osv

## Details
Vim is an open source, command line text editor. In versions from 9.1.1231 to before 9.1.1406, when processing nested tuples during Vim9 script import operations, an error during evaluation can trigger a double-free in Vim’s internal typed value (typval_T) management. Specifically, the clear_tv() function may attempt to free memory that has already been deallocated, due to improper lifetime handling in the handle_import / ex_import code paths. The vulnerability can only be triggered if a user explicitly opens and executes a specially crafted Vim script. This issue has been patched in version 9.1.1406.

## References
- https://github.com/vim/vim/releases/tag/v9.1.1406
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55158.json
- https://github.com/vim/vim/security/advisories/GHSA-5fg8-wvx3-583x
- https://nvd.nist.gov/vuln/detail/CVE-2025-55158
- https://github.com/vim/vim/commit/9772025d24e939fd84b85748ce35c26874c05775
