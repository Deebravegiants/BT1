# [H] containerd affected by a local privilege escalation via wide permissions on CRI directory

## Summary
Severity: High
Advisory: GHSA-pwhc-rpq9-4c8w
CVE: CVE-2024-25621
CWE: CWE-279
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-11-06
Source: https://github.com/advisories/GHSA-pwhc-rpq9-4c8w
Type: github-advisory

## Affected
- Go: `github.com/containerd/containerd` — affected >=0 <1.7.29
- Go: `github.com/containerd/containerd/v2` — affected >=0 <2.0.7
- Go: `github.com/containerd/containerd/v2` — affected >=2.1.0-beta.0 <2.1.5
- Go: `github.com/containerd/containerd/v2` — affected >=2.2.0-beta.0 <2.2.0

## Details
### Impact

An overly broad default permission vulnerability was found in containerd.

- `/var/lib/containerd` was created with the permission bits 0o711, while it should be created with 0o700
  - Allowed local users on the host to potentially access the metadata store and the content store
- `/run/containerd/io.containerd.grpc.v1.cri` was created with 0o755, while it should be created with 0o700
  - Allowed local users on the host to potentially access the contents of Kubernetes local volumes. The contents of volumes might include setuid binaries, which could allow a local user on the host to elevate privileges on the host.
- `/run/containerd/io.containerd.sandbox.controller.v1.shim` was created with 0o711, while it should be created with 0o700

The directory paths may differ depending on the daemon configuration.
When the `temp` directory path is specified in the daemon configuration, that directory was also created with 0o711, while it should be created with 0o700.

### Patches

This bug has been fixed in the following containerd versions:

* 2.2.0
* 2.1.5
* 2.0.7
* 1.7.29

Users should update to these versions to resolve the issue.
These updates automatically change the permissions of the existing directories.

> [!NOTE]
>
> `/run/containerd` and `/run/containerd/io.containerd.runtime.v2.task` are still created with 0o711.
> This is an expected behavior for supporting userns-remapped containers.

### Workarounds

The system administrator on the host can manually chmod the directories to not 
have group or world accessible permisisons:

```
chmod 700 /var/lib/containerd
chmod 700 /run/containerd/io.containerd.grpc.v1.cri
chmod 700 /run/containerd/io.containerd.sandbox.controller.v1.shim
```

An alternative mitigation would be to run containerd in [rootless mode](https://github.com/containerd/containerd/blob/main/docs/rootless.md).

### Credits

The containerd project would like to thank David Leadbeater for responsibly disclosing this issue in accordance with the [containerd security policy](https://github.com/containerd/project/blob/main/SECURITY.md).

### For more information

If you have any questions or comments about this advisory:

* Open an issue in [containerd](https://github.com/containerd/containerd/issues/new/choose)
* Email us at [security@containerd.io](mailto:security@containerd.io)

To report a security issue in containerd:

* [Report a new vulnerability](https://github.com/containerd/containerd/security/advisories/new)

## References
- https://github.com/containerd/containerd/security/advisories/GHSA-pwhc-rpq9-4c8w
- https://nvd.nist.gov/vuln/detail/CVE-2024-25621
- https://github.com/containerd/containerd/commit/7c59e8e9e970d38061a77b586b23655c352bfec5
- https://github.com/containerd/containerd
- https://github.com/containerd/containerd/blob/main/docs/rootless.md
