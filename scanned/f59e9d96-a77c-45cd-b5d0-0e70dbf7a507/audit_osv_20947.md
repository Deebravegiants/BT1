# [H] CVE-2021-3905

## Summary
Severity: High
Advisory: CVE-2021-3905
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-08-23
Source: https://osv.dev/vulnerability/CVE-2021-3905
Type: osv

## Details
A memory leak was found in Open vSwitch (OVS) during userspace IP fragmentation processing. An attacker could use this flaw to potentially exhaust available memory by keeping sending packet fragments.

## References
- https://access.redhat.com/security/cve/CVE-2021-3905
- https://security.gentoo.org/glsa/202311-16
- https://bugzilla.redhat.com/show_bug.cgi?id=2019692
- https://github.com/openvswitch/ovs-issues/issues/226
- https://github.com/openvswitch/ovs/commit/803ed12e31b0377c37d7aa8c94b3b92f2081e349
- https://ubuntu.com/security/CVE-2021-3905
