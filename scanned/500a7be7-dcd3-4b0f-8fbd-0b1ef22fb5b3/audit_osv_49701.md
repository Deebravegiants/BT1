# [H] CVE-2019-16413

## Summary
Severity: High
Advisory: CVE-2019-16413
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-09-19
Source: https://osv.dev/vulnerability/CVE-2019-16413
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.0.4. The 9p filesystem did not protect i_size_write() properly, which causes an i_size_read() infinite loop and denial of service on SMP systems.

## References
- https://support.f5.com/csp/article/K43239141?utm_source=f5support&amp%3Butm_medium=RSS
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.0.4
- https://security.netapp.com/advisory/ntap-20191004-0001/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=5e3cc1ee1405a7eb3487ed24f786dec01b4cbe1f
- https://patchwork.kernel.org/patch/10753365/
