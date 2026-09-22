# [H] Capsule vulnerable to privilege escalation by ServiceAccount deployed in a Tenant Namespace

## Summary
Severity: High
Advisory: GHSA-x45c-cvp8-q4fm
CVE: CVE-2022-46167
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-05
Source: https://github.com/advisories/GHSA-x45c-cvp8-q4fm
Type: github-advisory

## Affected
- Go: `github.com/clastix/capsule` — affected >=0 <0.1.3

## Details
Capsule implements a multi-tenant and policy-based environment in a Kubernetes cluster. A ServiceAccount deployed in a Tenant Namespace, when granted with `PATCH` capabilities on its own Namespace, is able to edit it and remove the Owner Reference, breaking the reconciliation of the Capsule Operator and removing all the enforcement like Pod Security annotations, Network Policies, Limit Range and Resource Quota items.

With that said, an attacker could detach the Namespace from a Tenant that is forbidding starting privileged Pods using the Pod Security labels by removing the OwnerReference, removing the enforcement labels, and being able to start privileged containers that would be able to start a generic Kubernetes privilege escalation.

### Patches

Patches have been released for version 0.1.3 and all users must upgrade to this release.

### Workarounds

N.A.

### References

N.A.

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [github.com/clastix/capsule](https://github.com/clastix/capsule)
* Reach out on [#capsule](https://kubernetes.slack.com/archives/C03GETTJQRL) channel available on Kubernetes Slack workspace

## References
- https://github.com/clastix/capsule/security/advisories/GHSA-x45c-cvp8-q4fm
- https://nvd.nist.gov/vuln/detail/CVE-2022-46167
- https://github.com/clastix/capsule/commit/1df430e71be8c4778c82eca3459978ad7d0b4b7b
- https://github.com/clastix/capsule/commit/75525ac19254b0c5111e34d7985e2be7bc8b1ac1
- https://github.com/clastix/capsule
- https://github.com/clastix/capsule/releases/tag/v0.1.3
