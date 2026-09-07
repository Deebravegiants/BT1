# [M] On a compromised node, the fluid-csi service account can be used to modify node specs

## Summary
Severity: Medium
Advisory: GHSA-93xx-cvmc-9w3v
CVE: CVE-2023-30840
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:H/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-05-09
Source: https://github.com/advisories/GHSA-93xx-cvmc-9w3v
Type: github-advisory

## Affected
- Go: `github.com/fluid-cloudnative/fluid` — affected >=0.7.0 <0.8.6

## Details
### Impact

If a malicious user gains control of a Kubernetes node running fluid csi pod (controlled by the `csi-nodeplugin-fluid` node-daemonset), he/she can leverage the fluid-csi service account to modify specs of all the nodes in the cluster. However, since this service account lacks "list node" permissions, the attacker may need to use other techniques to identify vulnerable nodes.

Once the attacker identifies and modifies the node specs, he/she can manipulate system-level-privileged components to access all secrets in the cluster or execute pods on other nodes. This allows he/she to elevate privileges beyond the compromised node and potentially gain full privileged access to the whole cluster.

To exploit this vulnerability, the attacker can make all other nodes unschedulable (for example, patch node with taints) and wait for system-critical components with high privilege to appear on the compromised node. However, this attack requires two prerequisites: a compromised node and identifying all vulnerable nodes through other means. Additionally, since the attack is passive and requires patience and luck, the severity of this finding is considered medium.

### Patches
For users who're using version < 0.8.6, >= 0.7.0, upgrade to v0.8.6.

### Workarounds
Delete the `csi-nodeplugin-fluid` daemonset in `fluid-system` namespace and avoid using CSI mode to mount FUSE file systems. Alternatively using sidecar mode to mount FUSE file systems is recommended. Refer to [the doc](https://github.com/fluid-cloudnative/fluid/blob/master/docs/en/samples/knative.md) to get a full example of how to use sidecar mode.

### References


Fixed by [Fix rbacs and limit CSI Plugin's node related access](https://github.com/fluid-cloudnative/fluid/commit/77c8110a3d1ec077ae2bce6bd88d296505db1550)

### Credits
Special thanks to the discoverers of this issue:

Nanzi Yang ([nzyang@stu.xidian.edu.cn](mailto:nzyang@stu.xidian.edu.cn))

## References
- https://github.com/fluid-cloudnative/fluid/security/advisories/GHSA-93xx-cvmc-9w3v
- https://nvd.nist.gov/vuln/detail/CVE-2023-30840
- https://github.com/fluid-cloudnative/fluid/commit/77c8110a3d1ec077ae2bce6bd88d296505db1550
- https://github.com/fluid-cloudnative/fluid/commit/91c05c32db131997b5ca065e869c9918a125c149
- https://github.com/fluid-cloudnative/fluid
- https://github.com/fluid-cloudnative/fluid/releases/tag/v0.8.6
