# [M] CVE-2019-20794

## Summary
Severity: Medium
Advisory: CVE-2019-20794
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-05-09
Source: https://osv.dev/vulnerability/CVE-2019-20794
Type: osv

## Details
An issue was discovered in the Linux kernel 4.18 through 5.6.11 when unprivileged user namespaces are allowed. A user can create their own PID namespace, and mount a FUSE filesystem. Upon interaction with this FUSE filesystem, if the userspace component is terminated via a kill of the PID namespace's pid 1, it will result in a hung task, and resources being permanently locked up until system reboot. This can result in resource exhaustion.

## References
- https://security.netapp.com/advisory/ntap-20200608-0001/
- http://www.openwall.com/lists/oss-security/2020/08/24/1
- https://github.com/sargun/fuse-example
- https://sourceforge.net/p/fuse/mailman/message/36598753/
