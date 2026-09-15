# [H] CVE-2021-29266

## Summary
Severity: High
Advisory: CVE-2021-29266
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-03-26
Source: https://osv.dev/vulnerability/CVE-2021-29266
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.11.9. drivers/vhost/vdpa.c has a use-after-free because v->config_ctx has an invalid value upon re-opening a character device, aka CID-f6bbf0010ba0.

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.11.9
- https://security.netapp.com/advisory/ntap-20210513-0005/
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/commit/?id=f6bbf0010ba004f5e90c7aefdebc0ee4bd3283b9
