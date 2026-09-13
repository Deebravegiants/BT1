# [M] Vim heap-use-after-free in src/arglist.c:207

## Summary
Severity: Medium
Advisory: CVE-2024-43374
Aliases: GHSA-2w8m-443v-cgvw
CVSS: 4.5 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2024-08-15
Source: https://osv.dev/vulnerability/CVE-2024-43374
Type: osv

## Details
The UNIX editor Vim prior to version 9.1.0678 has a use-after-free error in argument list handling. When adding a new file to the argument list, this triggers `Buf*` autocommands. If in such an autocommand the buffer that was just opened is closed (including the window where it is shown), this causes the window structure to be freed which contains a reference to the argument list that we are actually modifying. Once the autocommands are completed, the references to the window and argument list are no longer valid and as such cause an use-after-free. Impact is low since the user must either intentionally add some unusual autocommands that wipe a buffer during creation (either manually or by sourcing a malicious plugin), but it will crash Vim. The issue has been fixed as of Vim patch v9.1.0678.

## References
- http://www.openwall.com/lists/oss-security/2024/08/15/6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/43xxx/CVE-2024-43374.json
- https://github.com/vim/vim/security/advisories/GHSA-2w8m-443v-cgvw
- https://nvd.nist.gov/vuln/detail/CVE-2024-43374
- https://security.netapp.com/advisory/ntap-20240920-0004/
- https://github.com/vim/vim/commit/0a6e57b09bc8c76691b367a5babfb79b31b770e8
