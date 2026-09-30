# [M] KubeVirt Guest Agent DoS via Excessive Network Interface Reports

## Summary
Severity: Medium
Advisory: GHSA-25mh-hp8x-cgrv
CVE: CVE-2025-14525
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:L (CVSS_V3)
Published: 2026-01-26
Source: https://github.com/advisories/GHSA-25mh-hp8x-cgrv
Type: github-advisory

## Affected
- Go: `kubevirt.io/kubevirt` — affected >=0

## Details
A flaw was found in KubeVirt. A user within a virtual machine (VM), if the guest agent is active, can exploit this by causing the agent to report an excessive number of network interfaces. This action can overwhelm the system's ability to store VM configuration updates, effectively blocking changes to the Virtual Machine Instance (VMI). This allows the VM user to restrict the VM administrator's ability to manage the VM, leading to a Denial of Dervice for administrative operations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-14525
- https://access.redhat.com/security/cve/CVE-2025-14525
- https://bugzilla.redhat.com/show_bug.cgi?id=2421360
- https://github.com/kubevirt/kubevirt
- https://github.com/kubevirt/kubevirt/releases/tag/v1.7.0
