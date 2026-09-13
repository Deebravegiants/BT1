# [H] CVE-2022-4696

## Summary
Severity: High
Advisory: CVE-2022-4696
Aliases: A-264692298, ASB-A-264692298
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-11
Source: https://osv.dev/vulnerability/CVE-2022-4696
Type: osv

## Details
There exists a use-after-free vulnerability in the Linux kernel through io_uring and the IORING_OP_SPLICE operation. If IORING_OP_SPLICE is missing the IO_WQ_WORK_FILES flag, which signals that the operation won't use current->nsproxy, so its reference counter is not increased. This assumption is not always true as calling io_splice on specific files will call the get_uts function which will use current->nsproxy leading to invalidly decreasing its reference counter later causing the use-after-free vulnerability. We recommend upgrading to version 5.10.160 or above

## References
- https://security.netapp.com/advisory/ntap-20230223-0003/
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/commit/?h=linux-5.10.y&id=75454b4bbfc7e6a4dd8338556f36ea9107ddf61a
- https://kernel.dance/#75454b4bbfc7e6a4dd8338556f36ea9107ddf61a
