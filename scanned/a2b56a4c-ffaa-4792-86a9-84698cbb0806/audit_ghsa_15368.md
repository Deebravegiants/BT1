# [C] RBAC Roles for `etcd` created by Kamaji are not disjunct

## Summary
Severity: Critical
Advisory: GHSA-6r4j-4rjc-8vw5
CVE: CVE-2024-42480
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-08-12
Source: https://github.com/advisories/GHSA-6r4j-4rjc-8vw5
Type: github-advisory

## Affected
- Go: `github.com/clastix/kamaji` — affected >=0

## Details
### Summary
_Using an "open at the top" range definition in RBAC for etcd roles leads to some TCPs API servers being able to read, write and delete the data of other control planes._

### Details

The problematic code is this: https://github.com/clastix/kamaji/blob/8cdc6191242f80d120c46b166e2102d27568225a/internal/datastore/etcd.go#L19-L24

The range created by this RBAC setup code looks like this:

```
etcdctl role get example
Role example
KV Read:
	[/example/, \0)
KV Write:
	[/example/, \0)
```

The range end `\0` means "everything that comes after" in etcd, so potentially all the key prefixes of controlplanes with a name that comes after "example" when sorting lexically (e.g. `example1`, `examplf`, all the way to `zzzzzzz` if you will).

### PoC

1. Create two TCP in the same Namespace
2. Scale Kamaji to zero to avoid reconciliations
3. change the Kubernetes API Server `--etcd-prefix` flag value  to point to the other TCP datastore key
4. wait it for get it up and running
5. use `kubectl` and will notice you're reading and writing data of another Tenant

### Impact

Full control over other TCPs data, if you are able to obtain the name of other TCPs that use the same datastore and are able to obtain the user certificates used by your control plane (or you are able to configure the kube-apiserver Deployment, as shown in the PoC).

## References
- https://github.com/clastix/kamaji/security/advisories/GHSA-6r4j-4rjc-8vw5
- https://nvd.nist.gov/vuln/detail/CVE-2024-42480
- https://github.com/clastix/kamaji/commit/1731e8c2ed5148b125ecfbdf091ee177bd44f3db
- https://github.com/clastix/kamaji
- https://github.com/clastix/kamaji/blob/8cdc6191242f80d120c46b166e2102d27568225a/internal/datastore/etcd.go#L19-L24
