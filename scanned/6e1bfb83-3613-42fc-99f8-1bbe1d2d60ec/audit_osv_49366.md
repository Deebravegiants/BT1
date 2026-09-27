# [M] CVE-2019-11360

## Summary
Severity: Medium
Advisory: CVE-2019-11360
CVSS: 4.2 (CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-07-12
Source: https://osv.dev/vulnerability/CVE-2019-11360
Type: osv

## Details
A buffer overflow in iptables-restore in netfilter iptables 1.8.2 allows an attacker to (at least) crash the program or potentially gain code execution via a specially crafted iptables-save file. This is related to add_param_to_argv in xshared.c.

## References
- https://0day.work/cve-2019-11360-bufferoverflow-in-iptables-restore-v1-8-2/
- https://git.netfilter.org/iptables/commit/iptables/xshared.c?id=2ae1099a42e6a0f06de305ca13a842ac83d4683e
