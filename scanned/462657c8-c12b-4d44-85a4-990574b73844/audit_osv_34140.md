# [M] Vim heap use-after-free vulnerability when processing recursive tuple data types

## Summary
Severity: Medium
Advisory: CVE-2025-55157
Aliases: GHSA-3r4f-mm4w-wgg6
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2025-08-11
Source: https://osv.dev/vulnerability/CVE-2025-55157
Type: osv

## Details
Vim is an open source, command line text editor. In versions from 9.1.1231 to before 9.1.1400, When processing nested tuples in Vim script, an error during evaluation can trigger a use-after-free in Vim’s internal tuple reference management. Specifically, the tuple_unref() function may access already freed memory due to improper lifetime handling, leading to memory corruption. The exploit requires direct user interaction, as the script must be explicitly executed within Vim. This issue has been patched in version 9.1.1400.

## References
- https://github.com/vim/vim/releases/tag/v9.1.1400
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55157.json
- https://github.com/vim/vim/security/advisories/GHSA-3r4f-mm4w-wgg6
- https://nvd.nist.gov/vuln/detail/CVE-2025-55157
- https://github.com/vim/vim/commit/1307743697bbc46e1518abfea7f89caa95bcaf97
