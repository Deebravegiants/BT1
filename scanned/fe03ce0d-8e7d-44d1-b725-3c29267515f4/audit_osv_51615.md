# [M] CVE-2021-3573

## Summary
Severity: Medium
Advisory: CVE-2021-3573
CVSS: 6.4 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-08-13
Source: https://osv.dev/vulnerability/CVE-2021-3573
Type: osv

## Details
A use-after-free in function hci_sock_bound_ioctl() of the Linux kernel HCI subsystem was found in the way user calls ioct HCIUNBLOCKADDR or other way triggers race condition of the call hci_unregister_dev() together with one of the calls hci_sock_blacklist_add(), hci_sock_blacklist_del(), hci_get_conn_info(), hci_get_auth_info(). A privileged local user could use this flaw to crash the system or escalate their privileges on the system. This flaw affects the Linux kernel versions prior to 5.13-rc5.

## References
- http://www.openwall.com/lists/oss-security/2023/07/02/1
- https://bugzilla.redhat.com/show_bug.cgi?id=1966578
- https://git.kernel.org/pub/scm/linux/kernel/git/bluetooth/bluetooth.git/commit/?id=e305509e678b3a4af2b3cfd410f409f7cdaabb52
- https://www.openwall.com/lists/oss-security/2021/06/08/2
