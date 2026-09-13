# [M] CVE-2020-35499

## Summary
Severity: Medium
Advisory: CVE-2020-35499
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-02-19
Source: https://osv.dev/vulnerability/CVE-2020-35499
Type: osv

## Details
A NULL pointer dereference flaw in Linux kernel versions prior to 5.11 may be seen if sco_sock_getsockopt function in net/bluetooth/sco.c do not have a sanity check for a socket connection, when using BT_SNDMTU/BT_RCVMTU for SCO sockets. This could allow a local attacker with a special user privilege to crash the system (DOS) or leak kernel internal information.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1910048
