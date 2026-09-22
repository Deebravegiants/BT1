# [C] CVE-2023-38426

## Summary
Severity: Critical
Advisory: CVE-2023-38426
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2023-07-18
Source: https://osv.dev/vulnerability/CVE-2023-38426
Type: osv

## Details
An issue was discovered in the Linux kernel before 6.3.4. ksmbd has an out-of-bounds read in smb2_find_context_vals when create_context's name_len is larger than the tag length.

## References
- https://security.netapp.com/advisory/ntap-20230915-0010/
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.3.4
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/fs/ksmbd?id=02f76c401d17e409ed45bf7887148fcc22c93c85
