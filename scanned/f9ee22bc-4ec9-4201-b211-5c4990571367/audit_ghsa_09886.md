# [H] kcp's cache server is accessible without authentication or authorization checks

## Summary
Severity: High
Advisory: GHSA-3j3q-wp9x-585p
CVE: CVE-2026-39429
CWE: CWE-302, CWE-306, CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-3j3q-wp9x-585p
Type: github-advisory

## Affected
- Go: `github.com/kcp-dev/kcp` — affected >=0.30.0 <0.30.3
- Go: `github.com/kcp-dev/kcp` — affected >=0 <0.29.3

## Details
### Summary

The cache server is directly exposed by the root shard and has no authentication or authorization in place.
This allows anyone who can access the root shard to read and write to the cache server.

### Details

The cache server is routed in the pre-mux chain in the shard code. 
The preHandlerChainMux is handled before any authn/authz in the cache server: 
https://github.com/kcp-dev/kcp/blob/aaf93d59cbcd0cefb70d94bd8959ce390547c4a2/pkg/server/config.go#L514-L518

This results in the cache server being proxied before any authn/authz in the handler chain takes place.

### Attack Vectors

#### 1. Unauthenticated Read Access (Primary)
An attacker can read all replicated resources from the cache without any credentials. This exposes:

| Category | Resources | Severity | Reason |
|---|---|---|---|
| RBAC | clusterroles, clusterrolebindings (filtered by annotation) | High | Only subset with `internal.kcp.io/replicate` annotation: access rules, APIExport bind/content rules, WorkspaceType use rules. Reveals permission structure for API access and tenancy. Roles/RoleBindings NOT replicated. |
| Infrastructure | logicalclusters, shards | High | Reveals full cluster topology and shard configuration |
| API surface | apiexports, apiexportendpointslices, apiresourceschemas | High | Reveals all exported APIs and their network endpoints |
| Admission control | mutatingwebhookconfigurations, validatingwebhookconfigurations, validatingadmissionpolicies | High | Reveals admission policies, aids bypass |
| Tenancy | workspacetypes | Medium | Reveals workspace structure |
| Cache metadata | cachedobjects, cachedresources, cachedresourceendpointslices | Medium | Exposes cache state and resource endpoints |

#### 2. Write Access with Race Condition (Secondary)
The cache server allows full CRUD operations. While injected objects are cleaned up by the replication controller, a race condition exists that could allow temporary privilege escalation.

#### The race window:

1. Attacker POSTs a malicious ClusterRole + ClusterRoleBinding to the cache server
2. Cache etcd watch fires and notifies two consumers in parallel:
2.1. The authorization informer (CacheKubeSharedInformerFactory) updates its in-memory store — the GlobalAuthorizer and WorkspaceContentAuthorizer now see the injected RBAC rules
2.2. The replication controller's informer enqueues a reconcile to its workqueue
3. Replication controller worker dequeues, calls getLocalCopy() → not found, deletes the object

Between steps 2 and 3, any API request hitting the GlobalAuthorizer ([global_authorizer.go:89-101](https://github.com/kcp-dev/kcp/blob/aaf93d59c/pkg/authorization/global_authorizer.go#L89-L101)) would evaluate RBAC against a store that includes the attacker's injected rules. The authorization informer and the replication controller share the same CacheKubeSharedInformerFactory ([config.go:361](https://github.com/kcp-dev/kcp/blob/aaf93d59c/pkg/server/config.go#L361)), so the object is visible to authorization as soon as the informer cache updates — before the replication controller can process and delete it.

**Practical exploitability is low** — the window is sub-second, requiring the attacker to fire the privileged API request with precise timing. However, it could be automated in a tight loop. The workqueue rate limiter could also widen the window under load.

**Self-healing mechanism:** The replication controller acts as a self-healing mechanism. Objects injected into the cache are deleted almost instantly because:

Creating an object in cache triggers the cache informer
Replication controller reconciles, calls getLocalCopy() → not found
Controller calls deleteObject() on the cache copy ([replication_reconcile.go:157-168](https://github.com/kcp-dev/kcp/blob/aaf93d59c/pkg/reconciler/cache/replication/replication_reconcile.go#L157-L168))

### Replicatable 

Start a kcp root shard and query the cache server, e.g. with:

```sh
curl --insecure 'https://root.vespucci.genericcontrolplane.io:6443/services/cache/shards/root/clusters/root/apis/apis.kcp.io/v1alpha1'
```

### Workarounds

Network-level access control: Restrict access to /services/cache/* paths at the load balancer, reverse proxy, or firewall level.
External cache server: Deploy the cache server separately with its own kubeconfig (--cache-server-kubeconfig) and restrict network access to it.

### Impact

Who is affected: Any kcp deployment where the root shard is network-reachable by untrusted clients. This applies when:

- **Helm chart deployments:** Affected if the shard's Service or Ingress exposes port 6443 externally.
- **Operator deployments:** Affected if the Shard resource has spec.externalURL set (or spec.baseURL — externalURL defaults to baseURL if unset). When a shard has an external URL, clients route to it directly, exposing the /services/cache/* path.
- **Any deployment method:** If the root shard's --shard-external-url is set and reachable from untrusted networks, the cache server is exposed.

**Not affected:** Deployments where the root shard is behind a front-proxy and is not directly reachable. The front-proxy does not forward /services/cache/* requests.

**Write persistence:** The replication controller watches the cache informer and acts as a self-healing mechanism. Objects injected into the cache are deleted almost instantly (sub-second) because:

- Creating an object in cache triggers the cache informer
- Replication controller reconciles, calls getLocalCopy() → not found
- Controller calls deleteObject() on the cache copy ([replication_reconcile.go:157-168](https://github.com/kcp-dev/kcp/blob/aaf93d59c/pkg/reconciler/cache/replication/replication_reconcile.go#L157-L168))

## References
- https://github.com/kcp-dev/kcp/security/advisories/GHSA-3j3q-wp9x-585p
- https://nvd.nist.gov/vuln/detail/CVE-2026-39429
- https://github.com/kcp-dev/kcp
- https://github.com/kcp-dev/kcp/releases/tag/v0.29.3
- https://github.com/kcp-dev/kcp/releases/tag/v0.30.3
