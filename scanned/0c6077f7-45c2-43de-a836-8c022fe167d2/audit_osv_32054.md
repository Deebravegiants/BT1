# [M] cifs.upcall  makes an upcall to the wrong namespace in containerized environments

## Summary
Severity: Medium
Advisory: CVE-2025-2312
CVSS: 5.9 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2025-03-25
Source: https://osv.dev/vulnerability/CVE-2025-2312
Type: osv

## Details
A flaw was found in cifs-utils. When trying to obtain Kerberos credentials, the cifs.upcall program from the cifs-utils package makes an upcall to the wrong namespace in containerized environments. This issue may lead to disclosing sensitive data from the host's Kerberos credentials cache.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/2xxx/CVE-2025-2312.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-2312
- https://git.samba.org/?p=cifs-utils.git;a=commit;h=89b679228cc1be9739d54203d28289b03352c174
- https://web.git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/fs/smb?id=db363b0a1d9e6b9dc556296f1b1007aeb496a8cf
