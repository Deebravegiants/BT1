# [M] KubeVirt NULL pointer dereference flaw

## Summary
Severity: Medium
Advisory: GHSA-vjhf-6xfr-5p9g
CVE: CVE-2024-31420
CWE: CWE-476
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-04-03
Source: https://github.com/advisories/GHSA-vjhf-6xfr-5p9g
Type: github-advisory

## Affected
- Go: `kubevirt.io/kubevirt` — affected >=0

## Details
A NULL pointer dereference flaw was found in KubeVirt. This flaw allows an attacker who has access to a virtual machine guest on a node with DownwardMetrics enabled to cause a denial of service by issuing a high number of calls to vm-dump-metrics --virtio and then deleting the virtual machine.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-31420
- https://access.redhat.com/security/cve/CVE-2024-31420
- https://bugzilla.redhat.com/show_bug.cgi?id=2272951
- https://github.com/kubevirt/kubevirt
