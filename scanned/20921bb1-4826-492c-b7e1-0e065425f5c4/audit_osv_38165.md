# [H] ProFTPD ACL Bypass via /proc/self/root Path Prefix in RNFR

## Summary
Severity: High
Advisory: CVE-2026-35025
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-35025
Type: osv

## Details
ProFTPD through 1.3.9b and 1.3.10rc2 contains an access control bypass vulnerability that allows authenticated FTP users to circumvent Directory ACL restrictions by prefixing paths with /proc/self/root in the RNFR command handler. Attackers can exploit the unresolved symlink components in dir_canonical_path() to cause dir_check() to perform lexical path comparisons that match no configured Directory block, enabling rename operations on files in DenyAll-protected directories and subsequent retrieval of those files. Mitigation: Sessions configured with DefaultRoot (chroot) are not affected, as chroot changes the directory to which /proc/self/root resolves.

## References
- http://www.proftpd.org/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35025.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-35025
- https://www.vulncheck.com/advisories/proftpd-acl-bypass-via-proc-self-root-path-prefix-in-rnfr
- https://github.com/proftpd/proftpd
- https://github.com/proftpd/proftpd/issues/2170
