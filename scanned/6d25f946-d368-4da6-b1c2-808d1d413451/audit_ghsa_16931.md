# [H] CRI-O vulnerable to an arbitrary systemd property injection

## Summary
Severity: High
Advisory: GHSA-2cgq-h8xw-2v5j
CVE: CVE-2024-3154
CWE: CWE-77
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-30
Source: https://github.com/advisories/GHSA-2cgq-h8xw-2v5j
Type: github-advisory

## Affected
- Go: `github.com/cri-o/cri-o` — affected >=1.29.0 <1.29.4
- Go: `github.com/cri-o/cri-o` — affected >=1.28.0 <1.28.6
- Go: `github.com/cri-o/cri-o` — affected >=0 <1.27.6

## Details
### Impact
On CRI-O, it looks like an arbitrary systemd property can be injected via a Pod annotation:
```
---
apiVersion: v1
kind: Pod
metadata:
  name: poc-arbitrary-systemd-property-injection
  annotations:
    # I believe that ExecStart with an arbitrary command works here too,
    # but I haven't figured out how to marshalize the ExecStart struct to gvariant string.
    org.systemd.property.SuccessAction: "'poweroff-force'"
spec:
  containers:
    - name: hello
      image: [quay.io/podman/hello](http://quay.io/podman/hello)
```

This means that any user who can create a pod with an arbitrary annotation may perform an arbitrary action on the host system.

Tested with CRI-O v1.24 on minikube.
I didn't test the latest v1.29 because it is incompatible with minikube: https://github.com/kubernetes/minikube/pull/18367

Thanks to Cédric Clerget (GitHub ID @cclerget) for finding out that CRI-O just passes pod annotations to OCI annotations:
https://github.com/opencontainers/runc/pull/3923#discussion_r1532292536

CRI-O has to filter out annotations that have the prefix "org.systemd.property."

See also:
- https://github.com/opencontainers/runtime-spec/blob/main/features.md#unsafe-annotations-in-configjson
- https://github.com/opencontainers/runc/pull/4217


### Workarounds
Unfortunately, the only workarounds would involve an external mutating webhook to disallow these annotations

### References

## References
- https://github.com/cri-o/cri-o/security/advisories/GHSA-2cgq-h8xw-2v5j
- https://nvd.nist.gov/vuln/detail/CVE-2024-3154
- https://github.com/opencontainers/runc/pull/4217
- https://access.redhat.com/security/cve/CVE-2024-3154
- https://bugzilla.redhat.com/show_bug.cgi?id=2272532
- https://github.com/cri-o/cri-o
- https://github.com/opencontainers/runtime-spec/blob/main/features.md#unsafe-annotations-in-configjson
