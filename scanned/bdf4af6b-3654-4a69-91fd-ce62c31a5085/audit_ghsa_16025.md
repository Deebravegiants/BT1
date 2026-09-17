# [M] cert-manager ha a potential slowdown / DoS when parsing specially crafted PEM inputs

## Summary
Severity: Medium
Advisory: GHSA-r4pg-vg54-wxx4
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2024-11-20
Source: https://github.com/advisories/GHSA-r4pg-vg54-wxx4
Type: github-advisory

## Affected
- Go: `github.com/cert-manager/cert-manager` — affected >=0 <1.12.14
- Go: `github.com/cert-manager/cert-manager` — affected >=1.13.0-alpha.0 <1.15.4
- Go: `github.com/cert-manager/cert-manager` — affected >=1.16.0-alpha.0 <1.16.2

## Details
### Impact

cert-manager packages which call the standard library `pem.Decode()` function  can take a long time to process specially crafted invalid PEM data.

If an attacker is able to modify PEM data which cert-manager reads (e.g. in a Secret resource), they may be able to use large amounts of CPU in the cert-manager controller pod to effectively create a denial-of-service (DoS) vector for cert-manager in the cluster.

Secrets are limited in size to [1MiB](https://kubernetes.io/docs/concepts/configuration/secret/#restriction-data-size), which reduces the impact of this issue; it was discovered through an ~856kB fuzz test input which causes `pem.Decode` to take roughly 750ms to reject the input on an M2 Max Macbook Pro. By way of comparison, a valid PEM-encoded 4096-bit RSA key takes roughly 70µs to parse on the same machine.

Given the required size of PEM data needed to present a realistic DoS vector, an attacker would need to create or insert many different large sized resources in the cluster, and so the best secondary defense is to ensure that sensible limits are placed via RBAC.

This issue affects all versions of cert-manager to have been released since at least v0.1.0 (since `pem.Decode` is core functionality for cert-manager). All [supported releases](https://cert-manager.io/docs/releases/) are patched.

### Patches

The fixed versions are v1.16.2, v1.15.4 and v1.12.14.

- master branch: https://github.com/cert-manager/cert-manager/pull/7400
- release-1.16 branch: https://github.com/cert-manager/cert-manager/pull/7401
- release-1.15 branch: https://github.com/cert-manager/cert-manager/pull/7402
- release-1.12 branch: https://github.com/cert-manager/cert-manager/pull/7403

### Workarounds

Ensure that RBAC is scoped correctly in your cluster. If a user is able to modify resources containing PEM data to be able to exploit this, it's like that those permissions are a bigger security threat than this issue - especially for Secret resources.

### References

- Upstream issue: https://github.com/golang/go/issues/50116
- Similar issue: https://github.com/sigstore/sigstore/issues/198
- Google OSSFuzz: https://issues.oss-fuzz.com/issues/376728466

## References
- https://github.com/cert-manager/cert-manager/security/advisories/GHSA-r4pg-vg54-wxx4
- https://github.com/golang/go/issues/50116
- https://github.com/cert-manager/cert-manager/pull/7400
- https://github.com/cert-manager/cert-manager/pull/7401
- https://github.com/cert-manager/cert-manager/pull/7402
- https://github.com/cert-manager/cert-manager/pull/7403
- https://github.com/cert-manager/cert-manager/commit/3a4c9eb55e2e43570679840bbe3217869fbc8efc
- https://github.com/cert-manager/cert-manager/commit/f22f78c8c0a64d718e203b326bc844c488ad7850
- https://github.com/cert-manager/cert-manager
- https://go.dev/issue/50116
- https://pkg.go.dev/vuln/GO-2024-3282
