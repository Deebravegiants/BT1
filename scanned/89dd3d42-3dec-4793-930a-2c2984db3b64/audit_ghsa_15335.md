# [M] Gateway API route matching order contradicts specification

## Summary
Severity: Medium
Advisory: GHSA-qcm3-7879-xcww
CVE: CVE-2024-42487
CWE: CWE-113, CWE-436
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2024-08-15
Source: https://github.com/advisories/GHSA-qcm3-7879-xcww
Type: github-advisory

## Affected
- Go: `github.com/cilium/cilium` — affected >=1.16.0 <1.16.1
- Go: `github.com/cilium/cilium` — affected >=1.15.0 <1.15.8

## Details
### Impact

Gateway API HTTPRoutes and GRPCRoutes do not follow the match precedence specified in the Gateway API specification. In particular, request headers are matched before request methods, when the specification describes that the request methods must be respected before headers are matched ([HTTPRouteRule](https://gateway-api.sigs.k8s.io/reference/spec/#gateway.networking.k8s.io/v1.HTTPRouteRule), [GRPCRouteRule](https://gateway-api.sigs.k8s.io/reference/spec/#gateway.networking.k8s.io%2fv1.GRPCRouteRule)).

If users create Gateway API resources that use both request headers and request methods in order to route to different destinations, then traffic may be delivered to the incorrect backend. If the backend does not have Network Policy restricting acceptable traffic to receive, then requests may access information that you did not intend for them to access.

### Patches

This issue was fixed in https://github.com/cilium/cilium/pull/34109.

This issue affects:
- Cilium v1.15 between v1.15.0 and v1.15.7 inclusive
- Cilium v1.16.0

This issue is fixed in:
- Cilium v1.15.8
- Cilium v1.16.1

### Workarounds

There is no workaround for this issue.

### Acknowledgements

The Cilium community has worked together with members of Cure53 and Isovalent to prepare these mitigations. Special thanks to @sayboras for remediating this issue.

### Further information

If you have any questions or comments about this advisory, please reach out on [Slack](https://docs.cilium.io/en/latest/community/community/#slack).

If you think you have found a vulnerability affecting Cilium, we strongly encourage you to report it to our security mailing list at [security@cilium.io](mailto:security@cilium.io). This is a private mailing list for the Cilium security team, and your report will be treated as top priority.

## References
- https://github.com/cilium/cilium/security/advisories/GHSA-qcm3-7879-xcww
- https://nvd.nist.gov/vuln/detail/CVE-2024-42487
- https://github.com/cilium/cilium/pull/34109
- https://github.com/cilium/cilium/commit/a3510fe4a92305822aa1a5e08cb6d6c873c8699a
- https://github.com/cilium/cilium/commit/d88772b9c29e370becbc4547cada6711d51edcde
- https://github.com/cilium/cilium/commit/fe42273566a943a0f3174c87b23a195c856b51d6
- https://github.com/cilium/cilium
