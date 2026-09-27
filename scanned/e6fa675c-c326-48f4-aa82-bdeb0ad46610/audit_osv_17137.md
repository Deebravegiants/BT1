# [M] CVE-2020-12831

## Summary
Severity: Medium
Advisory: CVE-2020-12831
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-05-13
Source: https://osv.dev/vulnerability/CVE-2020-12831
Type: osv

## Details
An issue was discovered in FRRouting FRR (aka Free Range Routing) through 7.3.1. When using the split-config feature, the init script creates an empty config file with world-readable default permissions, leading to a possible information leak via tools/frr.in and tools/frrcommon.sh.in. NOTE: some parties consider this user error, not a vulnerability, because the permissions are under the control of the user before any sensitive information is present in the file

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1830805
- https://github.com/FRRouting/frr/pull/6383
