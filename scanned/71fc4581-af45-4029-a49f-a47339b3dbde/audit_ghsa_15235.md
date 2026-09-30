# [M] CRI-O's pods can break out of resource confinement on cgroupv2

## Summary
Severity: Medium
Advisory: GHSA-p4rx-7wvg-fwrc
CVE: CVE-2023-6476
CWE: CWE-400, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-01-10
Source: https://github.com/advisories/GHSA-p4rx-7wvg-fwrc
Type: github-advisory

## Affected
- Go: `github.com/cri-o/cri-o` — affected >=1.29.0 <1.29.1
- Go: `github.com/cri-o/cri-o` — affected >=1.28.0 <1.28.3
- Go: `github.com/cri-o/cri-o` — affected >=0 <1.27.3

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_
All versions of CRI-O running on cgroupv2 nodes. 
Unchecked access to an experimental annotation allows a container to be unconfined. Back in 2021, [support was added](https://github.com/cri-o/cri-o/pull/4479) to support an experimental annotation that allows a user to request special resources in cgroupv2. It was supposed to be gated by an experimental annotation: `io.kubernetes.cri-o.UnifiedCgroup`, which was supposed to be filtered from the [list of allowed annotations](https://github.com/cri-o/cri-o/blob/main/pkg/config/workloads.go#L103-L107) . However, there is a bug in this code which allows any user to specify this annotation, regardless of whether it's enabled on the node. The consequences of this are a pod can specify any amount of memory/cpu and get it, circumventing the kubernetes scheduler, and potentially be able to DOS a node. 
### Patches
_Has the problem been patched? What versions should users upgrade to?_
1.29.1, 1.28.3, 1.27.3

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_
use cgroupv1

### References
_Are there any links users can visit to find out more?_

## References
- https://github.com/cri-o/cri-o/security/advisories/GHSA-p4rx-7wvg-fwrc
- https://nvd.nist.gov/vuln/detail/CVE-2023-6476
- https://github.com/cri-o/cri-o/pull/4479
- https://github.com/cri-o/cri-o/commit/75effcb1a25851a736e82dba1f7d8cee93ee159e
- https://access.redhat.com/errata/RHSA-2024:0195
- https://access.redhat.com/errata/RHSA-2024:0207
- https://access.redhat.com/security/cve/CVE-2023-6476
- https://bugzilla.redhat.com/show_bug.cgi?id=2253994
- https://github.com/cri-o/cri-o
- https://github.com/cri-o/cri-o/blob/main/pkg/config/workloads.go#L103-L107
