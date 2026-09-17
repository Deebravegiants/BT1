# [H] Use after free in io_uring in the Linux Kernel

## Summary
Severity: High
Advisory: CVE-2023-0240
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-30
Source: https://osv.dev/vulnerability/CVE-2023-0240
Type: osv

## Details
There is a logic error in io_uring's implementation which can be used to trigger a use-after-free vulnerability leading to privilege escalation.

In the io_prep_async_work function the assumption that the last io_grab_identity call cannot return false is not true, and in this case the function will use the init_cred or the previous linked requests identity to do operations instead of using the current identity. This can lead to reference counting issues causing use-after-free. We recommend upgrading past version 5.10.161.

## References
- https://git.kernel.org
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/commit/io_uring?h=linux-5.10.y&id=788d0824269bef539fe31a785b1517882eafed93
- https://kernel.dance/#788d0824269bef539fe31a785b1517882eafed93
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/0xxx/CVE-2023-0240.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-0240
- https://security.netapp.com/advisory/ntap-20230316-0001/
- https://github.com/gregkh/linux/commit/1e6fa5216a0e59ef02e8b6b40d553238a3b81d49
