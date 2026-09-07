# [H] github.com/ctfer-io/monitoring Vulnerable to Improper Access Control

## Summary
Severity: High
Advisory: GHSA-7x23-j8gv-v54x
CVE: CVE-2026-32720
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:N/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-7x23-j8gv-v54x
Type: github-advisory

## Affected
- Go: `github.com/ctfer-io/monitoring` — affected >=0 <0.2.1

## Details
### Impact

Due to a mis-written NetworkPolicy, a malicious actor can pivot from a component to any other namespace.
This breaks the security-by-default property expected as part of the deployment program, leading to a potential lateral movement.

### Patch

Removing the `inter-ns` NetworkPolicy patches the vulnerability. If updates are not possible in production environments, we recommend to manually delete it and update as soon as possible.

### Workaround

Given your context, delete the failing network policy that should be prefixed by `inter-ns-` in the monitoring namespace.
You can use the following to delete all matching network policy. If unsure of the outcome, please do it manually.

```bash
for ns in $(kubectl get ns -o jsonpath='{.items[*].metadata.name}' | tr ' ' '\n' | grep '^monitoring-'); do
  kubectl -n "$ns" get networkpolicy -o name \
  | grep '^networkpolicy.networking.k8s.io/inter-ns-' \
  | xargs -r kubectl -n "$ns" delete
done
```

## References
- https://github.com/ctfer-io/monitoring/security/advisories/GHSA-7x23-j8gv-v54x
- https://nvd.nist.gov/vuln/detail/CVE-2026-32720
- https://github.com/ctfer-io/monitoring/pull/168
- https://github.com/ctfer-io/monitoring/commit/5404a11863b32b14ee5c62d1215352ab519d4edb
- https://github.com/ctfer-io/monitoring
- https://github.com/ctfer-io/monitoring/releases/tag/v0.2.1
