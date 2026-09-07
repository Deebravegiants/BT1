# [M] Source controller: Improper path handling allows traversal

## Summary
Severity: Medium
Advisory: GHSA-jjrm-hr5f-673x
CVE: CVE-2026-47680
CWE: CWE-23
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-05
Source: https://github.com/advisories/GHSA-jjrm-hr5f-673x
Type: github-advisory

## Affected
- Go: `github.com/fluxcd/source-controller` — affected >=0.0.17 <1.8.5

## Details
### Impact

An actor with the ability to influence the contents of a bucket referenced by a `Bucket` resource can cause source-controller to write fetched object data to paths outside the per-reconciliation working directory.

The corruption surface is bounded by source-controller's own and downstream Flux controllers' digest verification: source-controller verifies stored artifact digests during reconciliation and rebuilds on divergence; consumers (kustomize-controller, helm-controller) verify the digest of fetched artifacts and reject mismatches. These checks prevent a manipulated artifact from reaching the cluster, but an attacker can still write files anywhere the source-controller pod has permission to write.

Separately, a user with permission to create or update `GitRepository` resources can cause source-controller to test for the existence of paths outside the cloned repository. Because the result is exposed via the resource's status, this allows limited enumeration of file paths on the controller pod. This surface exists only on source-controller v1.6.0 and later, where the sparse-checkout feature was introduced.

### Patches

This vulnerability was fixed in source-controller **v1.8.5**.

### Workarounds

There is no in-product workaround. Users should upgrade to a patched version.

As a defense-in-depth measure for the GitRepository sparse-checkout surface, a `ValidatingAdmissionPolicy` (or a third-party policy engine such as Kyverno or OPA Gatekeeper) can be deployed to reject `GitRepository` resources whose `.spec.sparseCheckout` entries contain `..` or absolute path segments.

### References

- [source-controller#2054](https://github.com/fluxcd/source-controller/pull/2054)

### Credits

The path traversal in the Bucket reconciler was reported by JUNYI LIU. The path traversal in the GitRepository sparse-checkout validation was found and patched by the Flux engineering team.

### For more information

If you have any questions or comments about this advisory:

- Open an issue in the source-controller repository.
- Contact us at the CNCF Flux Channel.

## References
- https://github.com/fluxcd/source-controller/security/advisories/GHSA-jjrm-hr5f-673x
- https://github.com/fluxcd/source-controller/pull/2054
- https://github.com/fluxcd/source-controller/commit/759bd6c451e7cc4327b38f42c8b671980165cb0e
- https://github.com/fluxcd/source-controller
