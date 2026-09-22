# [H] Envoy Admin Interface Exposed through prometheus metrics endpoint

## Summary
Severity: High
Advisory: GHSA-j777-63hf-hx76
CVE: CVE-2025-24030
CWE: CWE-419
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H (CVSS_V3)
Published: 2025-01-23
Source: https://github.com/advisories/GHSA-j777-63hf-hx76
Type: github-advisory

## Affected
- Go: `github.com/envoyproxy/gateway` — affected >=0 <1.2.6

## Details
### Impact
A user with access to a Kubernetes cluster where Envoy Gateway is installed can use a path traversal attack to execute Envoy Admin interface commands on proxies managed by Envoy Gateway. The admin interface can be used to terminate the Envoy process and extract the Envoy configuration (possibly containing confidential data). 

For example, the following command, if run from within the Kubernetes cluster, can be used to get the configuration dump of the proxy:
```
curl --path-as-is http://<Proxy-Service-ClusterIP>:19001/stats/prometheus/../../config_dump
```
### Patches
1.2.6

### Workarounds
The `EnvoyProxy` API can be used to apply a bootstrap config patch that restricts access strictly to the prometheus stats endpoint. Find below an example of such a bootstrap patch. 

```
apiVersion: gateway.envoyproxy.io/v1alpha1
kind: EnvoyProxy
metadata:
  name: custom-proxy-config
  namespace: default
spec:
  bootstrap:
    type: JSONPatch
    jsonPatches:
    - op: "add"
      path: "/static_resources/listeners/0/filter_chains/0/filters/0/typed_config/normalize_path"
      value: true
    - op: "replace"
      path: "/static_resources/listeners/0/filter_chains/0/filters/0/typed_config/route_config/virtual_hosts/0/routes/0/match"
      value:
        path: "/stats/prometheus"
        headers:
          - name: ":method"
            exact_match: GET
```

### References
- Envoy Admin Interface: https://www.envoyproxy.io/docs/envoy/latest/operations/admin
- Envoy Configuration Best Practices: https://www.envoyproxy.io/docs/envoy/latest/configuration/best_practices/edge

## References
- https://github.com/envoyproxy/gateway/security/advisories/GHSA-j777-63hf-hx76
- https://nvd.nist.gov/vuln/detail/CVE-2025-24030
- https://github.com/envoyproxy/gateway/commit/3eb3301ab3dbf12b201b47bdb6074d1233be07bd
- https://github.com/envoyproxy/gateway
- https://www.envoyproxy.io/docs/envoy/latest/configuration/best_practices/edge
- https://www.envoyproxy.io/docs/envoy/latest/operations/admin
