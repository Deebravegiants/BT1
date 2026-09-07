# [H] Code Injection in CRI-O

## Summary
Severity: High
Advisory: GHSA-6x2m-w449-qwx7
CVE: CVE-2022-0811
CWE: CWE-94
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-15
Source: https://github.com/advisories/GHSA-6x2m-w449-qwx7
Type: github-advisory

## Affected
- Go: `github.com/cri-o/cri-o` — affected >=1.19.0 <1.19.6
- Go: `github.com/cri-o/cri-o` — affected >=1.20.0 <1.20.7
- Go: `github.com/cri-o/cri-o` — affected >=1.21.0 <1.21.6
- Go: `github.com/cri-o/cri-o` — affected >=1.22.0 <1.22.3
- Go: `github.com/cri-o/cri-o` — affected >=1.23.0 <1.23.2

## Details
### Impact
A flaw introduced in CRI-O version 1.19 which an attacker can use to bypass the safeguards and set arbitrary kernel parameters on the host. As a result, anyone with rights to deploy a pod on a Kubernetes cluster that uses the CRI-O runtime can abuse the `kernel.core_pattern` kernel parameter to achieve container escape and arbitrary code execution as root on any node in the cluster.

### Patches
The patches will be present in 1.19.6, 1.20.7, 1.21.6, 1.22.3, 1.23.2, 1.24.0

### Workarounds
- Users can set manage_ns_lifecycle to false, which causes the sysctls to be configured by the OCI runtime, which typically filter these cases. This option is available in 1.20 and 1.19. Newer versions don't have this option.
- An admission webhook could be created to deny pods that specify a `+` in the sysctl value of a pod.
- A [PodSecurityPolicy](https://kubernetes.io/docs/tasks/administer-cluster/sysctl-cluster/#podsecuritypolicy) [deprecated] could be created, specifying all sysctls as forbidden like so: 
```
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: sysctl-psp
spec:
  forbiddenSysctls:
    - "*"
```
However, this option will not work if any sysctls are required by any pods in the cluster.


### Credits
Credit for finding this vulnerability goes to John Walker and Manoj Ahuje of Crowdstrike. The CRI-O community deeply thanks them for the report.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [the CRI-O repo](http://github.com/cri-o/cri-o/issues)
* To make a report, email your vulnerability to the private
[cncf-crio-security@lists.cncf.io](mailto:cncf-crio-security@lists.cncf.io) list
with the security details and the details expected for [all CRI-O bug
reports](https://github.com/cri-o/cri-o/blob/main/.github/ISSUE_TEMPLATE/bug-report.yml).

## References
- https://github.com/cri-o/cri-o/security/advisories/GHSA-6x2m-w449-qwx7
- https://nvd.nist.gov/vuln/detail/CVE-2022-0811
- https://access.redhat.com/security/cve/CVE-2022-0811
- https://bugs.gentoo.org/835336
- https://bugzilla.redhat.com/show_bug.cgi?id=2059475
- https://github.com/cri-o/cri-o
- https://www.crowdstrike.com/blog/cr8escape-zero-day-vulnerability-discovered-in-cri-o-container-engine-cve-2022-0811
