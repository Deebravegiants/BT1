# [C] Local Path Provisioner vulnerable to Path Traversal via parameters.pathPattern

## Summary
Severity: Critical
Advisory: GHSA-jr3w-9vfr-c746
CVE: CVE-2025-62878
CWE: CWE-23
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-04
Source: https://github.com/advisories/GHSA-jr3w-9vfr-c746
Type: github-advisory

## Affected
- Go: `github.com/rancher/local-path-provisioner` — affected >=0 <0.0.34

## Details
### Impact

A malicious user can manipulate the [parameters.pathPattern](https://github.com/rancher/local-path-provisioner/blob/d4f71b4b03a321e9f54be00808e9de42b8bfd35a/provisioner.go#L381) to create PersistentVolumes in arbitrary locations on the host node, potentially overwriting sensitive files or gaining access to unintended directories.

Example:
```
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: >
      {"apiVersion":"storage.k8s.io/v1","kind":"StorageClass","metadata":{"annotations":{},"name":"local-path"},"provisioner":"rancher.io/local-path","reclaimPolicy":"Delete","volumeBindingMode":"WaitForFirstConsumer"}
    storageclass.kubernetes.io/is-default-class: 'true'
  name: local-path
provisioner: rancher.io/local-path
reclaimPolicy: Delete
parameters:
  pathPattern: "{{ .PVC.Namespace }}/{{ .PVC.Name }}/../../../../../etc/new-dir"
volumeBindingMode: WaitForFirstConsumer
Results in the PersistentVolume to target /etc/new-dir:
```
This produces a PersistentVolume that points to `/etc/new-dir`, instead of a path under the configured base directory.

Expected Behavior:
- Paths generated from pathPattern should always resolve under the configured base path.
- Relative path elements (e.g., ..) should be normalized or rejected.


### Patches

This vulnerability is addressed by validating and normalizing the `parameters.pathPattern` to ensure that generated PersistentVolume paths always resolve under the configured base directory. Any path traversal attempts using relative path elements are rejected, preventing PersistentVolumes from being created in arbitrary locations on the host node.

Previously, a malicious user could manipulate `pathPattern` to escape the base path and create volumes pointing to sensitive or unintended directories (for example, `/etc`), potentially overwriting host files or gaining unauthorized access.

With this fix, path patterns that resolve outside of the base directory are denied, and only safe, normalized paths under the configured base path are allowed.

Patched versions of local-path-provisioner include releases v0.0.34 (and later).

No patches are provided for earlier releases, as they do not include the necessary path validation and normalization logic.

### Workarounds

There are no workarounds for this issue. Users must upgrade to a patched version of local-path-provisioner to fully mitigate the vulnerability.

### References

There are any questions or comments about this advisory:

- Contact the [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security related inquiries.
- Open an issue in the [Rancher](https://github.com/rancher/rancher/issues/new/choose) repository.

## References
- https://github.com/rancher/local-path-provisioner/security/advisories/GHSA-jr3w-9vfr-c746
- https://nvd.nist.gov/vuln/detail/CVE-2025-62878
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2025-62878
- https://github.com/rancher/local-path-provisioner
- https://github.com/rancher/local-path-provisioner/blob/d4f71b4b03a321e9f54be00808e9de42b8bfd35a/provisioner.go#L381
