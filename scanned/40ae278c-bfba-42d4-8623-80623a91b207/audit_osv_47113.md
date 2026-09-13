# [M] CVE-2015-8956

## Summary
Severity: Medium
Advisory: CVE-2015-8956
CVSS: 6.1 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:L)
Published: 2016-10-10
Source: https://osv.dev/vulnerability/CVE-2015-8956
Type: osv

## Details
The rfcomm_sock_bind function in net/bluetooth/rfcomm/sock.c in the Linux kernel before 4.2 allows local users to obtain sensitive information or cause a denial of service (NULL pointer dereference) via vectors involving a bind system call on a Bluetooth RFCOMM socket.

## References
- http://rhn.redhat.com/errata/RHSA-2016-2574.html
- http://rhn.redhat.com/errata/RHSA-2016-2584.html
- http://source.android.com/security/bulletin/2016-10-01.html
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=951b6a0717db97ce420547222647bcc40bf1eacd
- http://source.android.com/security/bulletin/2016-10-01.html
- https://github.com/torvalds/linux/commit/951b6a0717db97ce420547222647bcc40bf1eacd
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=951b6a0717db97ce420547222647bcc40bf1eacd
- https://github.com/torvalds/linux/commit/951b6a0717db97ce420547222647bcc40bf1eacd
- http://www.securityfocus.com/bid/93326
