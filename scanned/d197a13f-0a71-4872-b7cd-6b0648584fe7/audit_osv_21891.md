# [H] CVE-2022-1199

## Summary
Severity: High
Advisory: CVE-2022-1199
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-08-29
Source: https://osv.dev/vulnerability/CVE-2022-1199
Type: osv

## Details
A flaw was found in the Linux kernel. This flaw allows an attacker to crash the Linux kernel by simulating amateur radio from the user space, resulting in a null-ptr-deref vulnerability and a use-after-free vulnerability.

## References
- https://access.redhat.com/security/cve/CVE-2022-1199
- https://www.openwall.com/lists/oss-security/2022/04/02/5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/1xxx/CVE-2022-1199.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-1199
- https://security.netapp.com/advisory/ntap-20221228-0006/
- https://bugzilla.redhat.com/show_bug.cgi?id=2070694
- https://github.com/torvalds/linux/commit/4e0f718daf97d47cf7dec122da1be970f145c809
- https://github.com/torvalds/linux/commit/71171ac8eb34ce7fe6b3267dce27c313ab3cb3ac
- https://github.com/torvalds/linux/commit/7ec02f5ac8a5be5a3f20611731243dc5e1d9ba10
