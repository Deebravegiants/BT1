# [H] @hulumi/policies bypasses IAM-role policy checks when the role trusts multiple OIDC providers

## Summary
Severity: High
Advisory: GHSA-g759-4pxw-6692
CVE: CVE-2026-48032
CWE: CWE-697
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-g759-4pxw-6692
Type: github-advisory

## Affected
- npm: `@hulumi/policies` — affected >=0 <1.4.0

## Details
**Affected:** `@hulumi/policies` `< 1.4.0` — **Fixed in:** `1.4.0` — **Severity:** High — **CWE-697 (Incorrect Comparison)**

#### Summary

AWS IAM trust policies can list more than one federated identity provider — for example, a role that accepts BOTH GitHub Actions OIDC and Google's OIDC. The `G_OIDC_1` and `G_OIDC_2` policy rules are supposed to flag IAM roles whose GitHub-OIDC trust is too permissive (e.g. wildcard `sub:` conditions that would let any branch or any pull request assume the role).

The bug: when the role's `Principal.Federated` field was a JSON array of multiple providers, the rules failed to recognise that GitHub Actions was one of them. The providers list was coerced into a single comma-joined string, the matcher only looked at the start, and the GitHub OIDC hostname was lost in the join. Both rules concluded "this isn't a GitHub-OIDC role" and skipped the wildcard check.

#### Impact

A trust policy that listed the real GitHub OIDC provider ARN alongside any second provider would slip past both detectors. Consumers using `HulumiHardeningPack` or `HulumiGithubHardeningPack` could ship an IAM role with wildcard `sub:` conditions (allowing untrusted PRs from forks to assume the role) while their policy validation reported the stack as compliant. The G_OIDC_2 detector also failed to mark such roles for the cluster-admin / `AdministratorAccess` blast-radius check.

#### Patches

Upgrade to `@hulumi/policies@1.4.0`. The shared GitHub-OIDC-provider matcher now correctly walks lists of providers — if any element of the list is the real GitHub OIDC ARN, the role is treated as GitHub-OIDC-assumable and the wildcard / blast-radius checks apply.

#### Workarounds

None reliable — upgrade is the fix.

#### Resources

- [PR #178](https://github.com/kerberosmansour/hulumi/pull/178) (Cluster A); regression tests at `packages/policies/tests/github/{g-oidc-2,github-oidc-issuer}.test.ts`.

## References
- https://github.com/kerberosmansour/hulumi/security/advisories/GHSA-g759-4pxw-6692
- https://github.com/kerberosmansour/hulumi/pull/178
- https://github.com/kerberosmansour/hulumi
