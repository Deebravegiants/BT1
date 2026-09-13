# [H] CVE-2022-2327

## Summary
Severity: High
Advisory: CVE-2022-2327
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-07-22
Source: https://osv.dev/vulnerability/CVE-2022-2327
Type: osv

## Details
io_uring use work_flags to determine which identity need to grab from the calling process to make sure it is consistent with the calling process when executing IORING_OP. Some operations are missing some types, which can lead to incorrect reference counts which can then lead to a double free. We recommend upgrading the kernel past commit df3f3bb5059d20ef094d6b2f0256c4bf4127a859

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/commit/?h=linux-5.10.y&id=df3f3bb5059d20ef094d6b2f0256c4bf4127a859
- https://kernel.dance/#df3f3bb5059d20ef094d6b2f0256c4bf4127a859
- https://security.netapp.com/advisory/ntap-20230203-0009/
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/commit/?h=linux-5.10.y&id=df3f3bb5059d20ef094d6b2f0256c4bf4127a859
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/commit/?h=linux-5.10.y&id=df3f3bb5059d20ef094d6b2f0256c4bf4127a859
- https://kernel.dance/#df3f3bb5059d20ef094d6b2f0256c4bf4127a859
