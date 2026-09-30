# [C] External Secrets Operator insecurely retrieves secrets through the getSecretKey templating function

## Summary
Severity: Critical
Advisory: GHSA-77v3-r3jw-j2v2
CVE: CVE-2026-22822
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-01-20
Source: https://github.com/advisories/GHSA-77v3-r3jw-j2v2
Type: github-advisory

## Affected
- Go: `github.com/external-secrets/external-secrets` — affected >=0.20.2 <1.2.0

## Details
### Summary

The `getSecretKey` template function, while introduced for senhasegura Devops Secrets Management (DSM) provider, has the ability to fetch secrets cross-namespaces with the roleBinding of the external-secrets controller, bypassing our security mechanisms.

This function was completely removed, as everything done with that templating function can be done in a different way while respecting our safeguards (for example, using `sourceRef` like explained here: https://github.com/external-secrets/external-secrets/issues/5690#issuecomment-3630977865)

### Impact
- Cross-namespace secret access: Attackers or misconfigured resources could retrieve secrets from namespaces other than the one intended.
- privilege escalation: Unauthorized access to secrets could lead to privilege escalation, data exfiltration, or compromise of service accounts and credentials.

### Resolution

We removed the incriminated templating function from our codebase. All users should upgrade to the latest version containing this fix.

### Workarounds

Use a policy engine such as Kubernetes, Kyverno, Kubewarden, or OPA to prevent the usage of `getSecretKey` in any ExternalSecret resource.

### Details

See also:
- https://github.com/external-secrets/external-secrets/issues/5690
- https://github.com/external-secrets/external-secrets/pull/3895

## References
- https://github.com/external-secrets/external-secrets/security/advisories/GHSA-77v3-r3jw-j2v2
- https://nvd.nist.gov/vuln/detail/CVE-2026-22822
- https://github.com/external-secrets/external-secrets/issues/5690
- https://github.com/external-secrets/external-secrets/pull/3895
- https://github.com/external-secrets/external-secrets/commit/17d3e22b8d3fbe339faf8515a95ec06ec92b1feb
- https://github.com/external-secrets/external-secrets
- https://github.com/external-secrets/external-secrets/releases/tag/v1.2.0
