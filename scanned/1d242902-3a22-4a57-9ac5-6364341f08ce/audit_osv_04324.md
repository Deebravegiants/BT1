# [H] Denial of service in Contour

## Summary
Severity: High
Advisory: BIT-contour-2020-15127
Aliases: CVE-2020-15127, GHSA-mjp8-x484-pm3r
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-contour-2020-15127
Type: osv

## Affected
- Bitnami: `contour` — affected >=0 <1.7.0

## Details
In Contour ( Ingress controller for Kubernetes) before version 1.7.0, a bad actor can shut down all instances of Envoy, essentially killing the entire ingress data plane. GET requests to /shutdown on port 8090 of the Envoy pod initiate Envoy's shutdown procedure. The shutdown procedure includes flipping the readiness endpoint to false, which removes Envoy from the routing pool. When running Envoy (For example on the host network, pod spec hostNetwork=true), the shutdown manager's endpoint is accessible to anyone on the network that can reach the Kubernetes node that's running Envoy. There is no authentication in place that prevents a rogue actor on the network from shutting down Envoy via the shutdown manager endpoint. Successful exploitation of this issue will lead to bad actors shutting down all instances of Envoy, essentially killing the entire ingress data plane. This is fixed in version 1.7.0.

## References
- https://github.com/projectcontour/contour/releases/tag/v1.7.0
- https://github.com/projectcontour/contour/security/advisories/GHSA-mjp8-x484-pm3r
- https://nvd.nist.gov/vuln/detail/CVE-2020-15127
