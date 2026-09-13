# [H] Local Path Provisioner Vulnerable to HelperPod Template Injection

## Summary
Severity: High
Advisory: GHSA-7fxv-8wr2-mfc4
CVE: CVE-2026-44543
CWE: CWE-1336, CWE-269
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-7fxv-8wr2-mfc4
Type: github-advisory

## Affected
- Go: `github.com/rancher/local-path-provisioner` — affected >=0 <0.0.36

## Details
### Impact

A malicious user with permission to edit the `local-path-config` ConfigMap in the `local-path-storage` namespace can manipulate the `helperPod.yaml` template used by `rancher/local-path-provisioner`.

The `helperPod.yaml` template is loaded by the provisioner and used to create HelperPods during PVC provisioning and cleanup operations. However, the template is not sufficiently validated before use. Security-sensitive fields such as `securityContext.privileged`, `hostPath` volumes, and Linux capabilities can be injected into the template.

Example malicious HelperPod template:

~~~yaml
apiVersion: v1
kind: Pod
metadata:
  name: helper-pod
spec:
  containers:
  - name: helper-pod
    image: docker.io/kindest/local-path-helper:v20230510-486859a6
    imagePullPolicy: IfNotPresent
    securityContext:
      privileged: true
    volumeMounts:
    - name: host-root
      mountPath: /host
  volumes:
  - name: host-root
    hostPath:
      path: /
      type: Directory
~~~

When a PVC operation triggers HelperPod creation, the provisioner creates the HelperPod using the attacker-controlled template. This can result in a privileged pod running on the target node with the host root filesystem mounted.

This may allow the attacker to access sensitive host files, read ServiceAccount tokens from other pods on the same node, access other tenants' local-path volume data, or modify files on the host node.

Expected Behavior:

- The HelperPod template should not allow privileged containers.
- The HelperPod template should not allow arbitrary `hostPath` mounts.
- Security-sensitive fields in `helperPod.yaml` should be validated or rejected before the provisioner creates HelperPods.

### Patches

This vulnerability is addressed by validating the HelperPod template loaded from the `local-path-config` ConfigMap before it is used to create HelperPods.

The fix ensures that unsafe fields such as privileged security contexts, hostPath volumes, and other dangerous pod security settings are rejected. This prevents an attacker with ConfigMap edit permission from injecting a malicious HelperPod template that grants access to the host node.

Previously, a malicious user could modify `helperPod.yaml` to cause the provisioner to create a privileged HelperPod with the host root filesystem mounted, potentially leading to node-level compromise and ServiceAccount token theft.

With this fix, HelperPod templates containing unsafe security-sensitive fields are denied, and only safe HelperPod configurations are accepted.

Patched versions of local-path-provisioner include releases v0.0.34 and later.

No patches are provided for earlier releases, as they do not include the necessary HelperPod template validation logic.

### Workarounds

Users should upgrade to a patched version of local-path-provisioner to fully mitigate this vulnerability.

As a temporary mitigation, users can restrict write access to the `local-path-config` ConfigMap in the `local-path-storage` namespace. Only trusted administrators should be allowed to update this ConfigMap.

Users may also mark the ConfigMap as immutable after deployment:

~~~bash
kubectl -n local-path-storage patch configmap local-path-config \
  --type merge -p '{"immutable": true}'
~~~

Additionally, enabling Kubernetes Pod Security Admission for the `local-path-storage` namespace can provide defense in depth. For example, enforcing the `baseline` policy can prevent privileged HelperPods from being created even if the template is modified:

~~~bash
kubectl label namespace local-path-storage \
  pod-security.kubernetes.io/enforce=baseline \
  pod-security.kubernetes.io/warn=restricted
~~~

These mitigations reduce the risk of exploitation, but upgrading to a patched release is required to fully address the issue.

### References

If you have any questions or comments about this advisory:

- Contact the [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security related inquiries.
- Open an issue in the [Rancher](https://github.com/rancher/rancher/issues/new/choose) repository.

## References
- https://github.com/rancher/local-path-provisioner/security/advisories/GHSA-7fxv-8wr2-mfc4
- https://nvd.nist.gov/vuln/detail/CVE-2026-44543
- https://github.com/rancher/local-path-provisioner
