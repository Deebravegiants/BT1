# [M] Kong Mesh: a dataplane token without a workload binding can claim any workload's SPIFFE identity

## Summary
Severity: Medium
Advisory: CVE-2026-18677
Aliases: GHSA-744g-c785-x65q
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-18677
Type: osv

## Details
In Kong Mesh running in universal mode with a MeshIdentity whose SPIFFE ID path template derives from the dataplane's kuma.io/workload label, the XDS authenticator in kuma-cp validates that label only when the dataplane token is bound to a workload. Workload binding is optional, so a dataplane presenting a tags-bound token can register with kuma.io/workload set to any value and obtain another workload's SPIFFE identity.

## References
- https://developer.konghq.com/mesh/changelog/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18677.json
- https://github.com/kumahq/kuma/security/advisories/GHSA-744g-c785-x65q
- https://nvd.nist.gov/vuln/detail/CVE-2026-18677
- https://github.com/kumahq/kuma/pull/17474
- https://github.com/kumahq/kuma/pull/17502
- https://github.com/kumahq/kuma/pull/17503
