# [M] Sealed Secrets for Kubernetes: Rotate API Allows Scope Widening from Strict/Namespace-Wide to Cluster-Wide via Untrusted Template Annotations

## Summary
Severity: Medium
Advisory: GHSA-465p-v42x-3fmj
CVE: CVE-2026-22728
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-02-26
Source: https://github.com/advisories/GHSA-465p-v42x-3fmj
Type: github-advisory

## Affected
- Go: `github.com/bitnami-labs/sealed-secrets` — affected >=0 <0.36.0

## Details
This report shows a scope-widening issue in the rotate (re-encrypt) flow: the output scope can be derived from untrusted `spec.template.metadata.annotations` on the input sealed secret.

If a victim sealed secret is strict- or namespace-scoped, an attacker who can submit it to the rotate endpoint can set `sealedsecrets.bitnami.com/cluster-wide=true` in the template metadata and receive a rotated sealed secret that is cluster-wide, enabling retargeting (`metadata.name`/`metadata.namespace`) and unsealing to recover the victim plaintext.

## Relevant Links (Pinned)

- Rotate handler uses `NewSealedSecret(..., secret)` after unsealing: https://github.com/bitnami-labs/sealed-secrets/blob/946bc048f3407117c837da6e4300686522d4c4eb/pkg/controller/controller.go#L560-L606
- Scope derivation reads secret annotations (`SecretScope`): https://github.com/bitnami-labs/sealed-secrets/blob/946bc048f3407117c837da6e4300686522d4c4eb/pkg/apis/sealedsecrets/v1alpha1/sealedsecret_expansion.go#L112-L122

## Root Cause

The rotate flow unseals the input sealed secret to a `Secret`, then reseals using `NewSealedSecret(..., secret)`.

Because `SecretScope(secret)` is computed from secret annotations, and unsealing applies `spec.template` metadata onto the unsealed secret, an attacker can influence the scope of the rotated output by mutating template annotations on the rotate input.

## Attack Path

1. Attacker obtains a victim `SealedSecret` object (for example via read access to resources or logs) and can submit it to the controller rotate endpoint.
2. Attacker sets `spec.template.metadata.annotations.sealedsecrets.bitnami.com/cluster-wide=true` (and optionally retargets name/namespace fields).
3. Rotate returns a resealed, cluster-wide sealed secret that is no longer bound to the victim name/namespace.
4. Attacker unseals the rotated output in their chosen namespace/name to recover the victim plaintext.

## Proof of Concept

Setup + run:

```bash
unzip poc.zip -d poc
cd poc
make test
```

Canonical output (excerpt):

```
[CALLSITE_HIT]: pkg/apis/sealedsecrets/v1alpha1/sealedsecret_expansion.go:112 SecretScope
[PROOF_MARKER]: scope_widened=true rotated_scope=cluster-wide
```

Control output (excerpt):

```
[NC_MARKER]: scope_widened=false strict_scope_preserved=true
```

## Fix Accepted When

Rotate preserves the original sealing scope and does not allow scope widening based on untrusted template metadata; strict or namespace-wide inputs cannot produce cluster-wide outputs.

[poc.zip](https://github.com/user-attachments/files/25080027/poc.zip)
[PR_DESCRIPTION.md](https://github.com/user-attachments/files/25080028/PR_DESCRIPTION.md)
[attack_scenario.md](https://github.com/user-attachments/files/25080029/attack_scenario.md)

## References
- https://github.com/bitnami-labs/sealed-secrets/security/advisories/GHSA-465p-v42x-3fmj
- https://nvd.nist.gov/vuln/detail/CVE-2026-22728
- https://github.com/bitnami-labs/sealed-secrets/commit/d57ee4a8357d250e602b995399b525496ab688c1
- https://github.com/bitnami-labs/sealed-secrets
- https://github.com/bitnami-labs/sealed-secrets/releases/tag/v0.36.0
