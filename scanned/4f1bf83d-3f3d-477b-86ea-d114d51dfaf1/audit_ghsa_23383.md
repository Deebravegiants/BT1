# [H] Access to Unix domain socket can lead to privileges escalation in Cilium

## Summary
Severity: High
Advisory: GHSA-6p8v-8cq8-v2r3
CVE: CVE-2022-29178
CWE: CWE-276
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-6p8v-8cq8-v2r3
Type: github-advisory

## Affected
- Go: `github.com/cilium/cilium` — affected >=1.11.0 <1.11.5
- Go: `github.com/cilium/cilium` — affected >=1.10.0 <1.10.11
- Go: `github.com/cilium/cilium` — affected >=0 <1.9.16

## Details
### Impact

Users with host file system access on a node and the privileges to run as group ID 1000 can gain access to the per node API of Cilium via Unix domain socket on the host where Cilium is running. If a malicious user is able to gain unprivileged access to a user corresponding to this group, then they can leverage this access to compromise the integrity as well as system availability on that host. Operating Systems that have unprivileged users **not** belonging the group ID 1000 are **not** affected by this vulnerability.

Best practices for managing the secure deployment of Kubernetes clusters will typically limit the ability for a malicious user to deploy pods with access to this group or to access the host filesystem, and limit user access to the nodes for users belonging to this group. These best practices include (but are not limited to) enforcing Admission Control policies to limit the configuration of Kubernetes Pod [hostPath](https://kubernetes.io/docs/concepts/storage/volumes/#hostpath) and [SecurityContext](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/) fields.

### Patches

Cilium versions >=1.9.16, >=1.10.11, >=1.11.5 mitigate this issue by setting the default group to 0 (root).

### Workarounds

Prevent Cilium from running with group 1000 by modifying Cilium's DaemonSet to run with the following command:

```yaml
      containers:
      - name: cilium-agent
        args:
        - -c
        - "groupdel cilium && cilium-agent --config-dir=/tmp/cilium/config-map"
        command:
        - bash
```
instead of
```yaml
      containers:
      - name: cilium-agent
        args:
        - --config-dir=/tmp/cilium/config-map
        command:
        - cilium-agent
```

### Acknowledgements

The Cilium community has worked together with members of Isovalent and Form 3 to prepare these mitigations.  Special thanks to Daniel Iziourov and Daniel Teixeira for their cooperation.

### For more information
If you have any questions or comments about this advisory:
* Email us at [security@cilium.io](mailto:security@cilium.io)

## References
- https://github.com/cilium/cilium/security/advisories/GHSA-6p8v-8cq8-v2r3
- https://nvd.nist.gov/vuln/detail/CVE-2022-29178
- https://github.com/cilium/cilium/releases/tag/v1.10.11
- https://github.com/cilium/cilium/releases/tag/v1.11.5
- https://github.com/cilium/cilium/releases/tag/v1.9.16
- github.com/cilium/cilium
