# [M] CVE-2021-20177

## Summary
Severity: Medium
Advisory: CVE-2021-20177
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-05-26
Source: https://osv.dev/vulnerability/CVE-2021-20177
Type: osv

## Details
A flaw was found in the Linux kernel's implementation of string matching within a packet. A privileged user (with root or CAP_NET_ADMIN) when inserting iptables rules could insert a rule which can panic the system. Kernel before kernel 5.5-rc1 is affected.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1914719
