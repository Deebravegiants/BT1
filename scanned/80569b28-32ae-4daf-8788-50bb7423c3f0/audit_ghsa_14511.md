# [H] On a compromised node, the virt-handler service account can be used to modify all node specs

## Summary
Severity: High
Advisory: GHSA-cp96-jpmq-xrr2
CVE: CVE-2023-26484
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2023-03-16
Source: https://github.com/advisories/GHSA-cp96-jpmq-xrr2
Type: github-advisory

## Affected
- Go: `kubevirt.io/kubevirt` — affected >=0

## Details
### Impact

If a malicious user has taken over a Kubernetes node where virt-handler (the KubeVirt node-daemon) is running, the virt-handler service account can be used to modify all node specs.

This can be misused to lure-in system-level-privileged components (which can for instance read all secrets on the cluster, or can exec into pods on other nodes). This way a compromised node can be used to elevate privileges beyond the node until potentially having full privileged access to the whole cluster.

The simplest way to exploit this, once a user could compromise a specific node, is to set with the virt-handler service account all other nodes to unschedulable and simply wait until system-critical components with high privileges appear on its node.

Since this requires a node to be compromised first, the severity of this finding is considered Medium.

### Patches

Not yet available.

### Workarounds
Gatekeeper users can add a webhook which will block the `virt-handler` service account to modify the spec of a node.

An example policy, preventing virt-handler from changing the node spec may look like this:

```yaml
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: virthandlerrestrictions
spec:
[...]
  targets:
    - libs:
        - |         
[...]          
          is_virt_handler(username) {
              username == "system:serviceaccount:kubevirt:virt-handler"
          }
          mutates_node_in_unintended_way {
            # TODO
            # only allow kubevirt.io/ prefixed metadata node changes
          }
      rego: |
[...]
        
        violation[{"msg": msg}] {
          is_virt_handler(username)
          mutates_node_in_unintended_way(input.review.object, input.review.oldObject)
          msg := sprintf("virt-handler tries to modify node <%v> in an unintended way.", [input.review.object.name])
        }
```

and applying this template to node modifications.


### Credits

Special thanks to the discoverers of this issue:

Nanzi Yang (nzyang@stu.xidian.edu.cn)
Xin Guo (guox@stu.xidian.edu.cn)
Jietao Xiao (jietaoXiao@stu.xidian.edu.cn)
Wenbo Shen (shenwenbo@zju.edu.cn)
Jinku Li (jkli@xidian.edu.cn)

### References

https://github.com/kubevirt/kubevirt/issues/9109

## References
- https://github.com/kubevirt/kubevirt/security/advisories/GHSA-cp96-jpmq-xrr2
- https://nvd.nist.gov/vuln/detail/CVE-2023-26484
- https://github.com/kubevirt/kubevirt/issues/9109
- https://github.com/kubevirt/kubevirt
