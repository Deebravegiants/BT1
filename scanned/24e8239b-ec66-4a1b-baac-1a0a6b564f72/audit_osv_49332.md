# [M] CVE-2019-10153

## Summary
Severity: Medium
Advisory: CVE-2019-10153
CVSS: 5.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:L)
Published: 2019-07-30
Source: https://osv.dev/vulnerability/CVE-2019-10153
Type: osv

## Details
A flaw was discovered in fence-agents, prior to version 4.3.4, where using non-ASCII characters in a guest VM's comment or other fields would cause fence_rhevm to exit with an exception. In cluster environments, this could lead to preventing automated recovery or otherwise denying service to clusters of which that VM is a member.

## References
- https://access.redhat.com/errata/RHSA-2019:2037
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10153
- https://github.com/ClusterLabs/fence-agents/pull/255
- https://github.com/ClusterLabs/fence-agents/pull/272
