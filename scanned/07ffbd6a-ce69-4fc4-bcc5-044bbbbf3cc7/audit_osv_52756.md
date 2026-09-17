# [M] CVE-2022-1016

## Summary
Severity: Medium
Advisory: CVE-2022-1016
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-08-29
Source: https://osv.dev/vulnerability/CVE-2022-1016
Type: osv

## Details
A flaw was found in the Linux kernel in net/netfilter/nf_tables_core.c:nft_do_chain, which can cause a use-after-free. This issue needs to handle 'return' with proper preconditions, as it can lead to a kernel information leak problem caused by a local, unprivileged attacker.

## References
- https://access.redhat.com/security/cve/CVE-2022-1016
- https://bugzilla.redhat.com/show_bug.cgi?id=2066614
- http://blog.dbouman.nl/2022/04/02/How-The-Tables-Have-Turned-CVE-2022-1015-1016/
- https://seclists.org/oss-sec/2022/q1/205
