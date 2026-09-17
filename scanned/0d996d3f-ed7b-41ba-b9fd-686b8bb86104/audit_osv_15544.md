# [H] CVE-2019-16995

## Summary
Severity: High
Advisory: CVE-2019-16995
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-09-30
Source: https://osv.dev/vulnerability/CVE-2019-16995
Type: osv

## Details
In the Linux kernel before 5.0.3, a memory leak exits in hsr_dev_finalize() in net/hsr/hsr_device.c if hsr_add_port fails to add a port, which may cause denial of service, aka CID-6caabe7f197d.

## References
- https://security.netapp.com/advisory/ntap-20191031-0005/
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00010.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00035.html
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=6caabe7f197d3466d238f70915d65301f1716626
- https://github.com/torvalds/linux/commit/6caabe7f197d3466d238f70915d65301f1716626
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.0.3
