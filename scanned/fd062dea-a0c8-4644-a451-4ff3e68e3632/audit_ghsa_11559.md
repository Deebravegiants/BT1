# [H] etcd: Authorization bypasses in multiple APIs

## Summary
Severity: High
Advisory: GHSA-q8m4-xhhv-38mg
CVE: CVE-2026-33413
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-q8m4-xhhv-38mg
Type: github-advisory

## Affected
- Go: `go.etcd.io/etcd/v3` — affected >=3.6.0-alpha.0 <3.6.9
- Go: `go.etcd.io/etcd/v3` — affected >=3.5.0-alpha.0 <3.5.28
- Go: `go.etcd.io/etcd/v3` — affected >=0 <3.4.42
- Go: `go.etcd.io/etcd` — affected >=0

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

Multiple vulnerabilities allow unauthorized users to bypass authentication or authorization checks and call certain etcd functions in clusters that expose the gRPC API to untrusted or partially trusted clients.

In unpatched etcd clusters with etcd auth enabled, unauthorized users are able to:

  - call MemberList and learn cluster topology, including member IDs and advertised endpoints
  - call Alarm, which can be abused for operational disruption or denial of service
  - use Lease APIs, interfering with TTL-based keys and lease ownership
  - trigger compaction, permanently removing historical revisions and disrupting watch, audit, and recovery workflows

Kubernetes does not rely on etcd’s built-in authentication and authorization. Instead, the API server handles authentication and authorization itself, so typical Kubernetes deployments are not affected.

### Patches
_Has the problem been patched? What versions should users upgrade to?_

These vulnerabilities are patched in the following versions:

* etcd 3.6.9
* etcd 3.5.28
* etcd 3.4.42

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

If upgrading is not immediately possible, reduce exposure by treating the affected 
RPCs as unauthenticated in practice.

- restrict network access to etcd server ports so only trusted components can connect
- require strong client identity at the transport layer, such as mTLS with tightly scoped client certificate
    distribution

### Reporters
_Community efforts help keep etcd secure_

The etcd community thanks Isaac David, bugbunny.ai, Asim Viladi Oglu Manizada, Alex Schapiro & Ahmed Allam from Strix security, Luke Francis, and @OLU-DEVX for reporting these vulnerabilities.

### Dependency Between Reported Issues

These issues all originate from the same underlying flaw in the gRPC API layer.

They affect the same API surface and share a common root cause. In practice, the fix is implemented as a single, unified change at the API layer, which resolves all issues together.

Given this, we believe these issues are best treated as a single vulnerability and should be assigned a single CVE.

## References
- https://github.com/etcd-io/etcd/security/advisories/GHSA-q8m4-xhhv-38mg
- https://nvd.nist.gov/vuln/detail/CVE-2026-33413
- https://github.com/etcd-io/etcd
