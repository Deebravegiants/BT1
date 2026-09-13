# [M] secrets-store-sync-controller discloses service account tokens in logs

## Summary
Severity: Medium
Advisory: GHSA-rcw7-pqfp-735x
CVE: CVE-2025-7445
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2025-09-05
Source: https://github.com/advisories/GHSA-rcw7-pqfp-735x
Type: github-advisory

## Affected
- Go: `sigs.k8s.io/secrets-store-sync-controller` — affected >=0 <0.0.2

## Details
Hello Kubernetes Community,

A security issue was discovered in secrets-store-sync-controller where an actor with access to the controller logs could observe service account tokens.  These tokens could then potentially be exchanged with external cloud providers to access secrets stored in cloud vault solutions.  Tokens are only logged when there is a specific error marshaling the `parameters` sent to the providers.

### Am I vulnerable?

To check if tokens are being logged, examine the manager container log:

```bash
kubectl logs -l 'app.kubernetes.io/part-of=secrets-store-sync-controller' -c manager -f | grep --line-buffered "csi.storage.k8s.io/serviceAccount.tokens"
```

### Affected Versions

- secrets-store-sync-controller < v0.0.2

### How do I mitigate this vulnerability?

Upgrade to secrets-store-sync-controller v0.0.2+

### Fixed Versions

- secrets-store-sync-controller >= v0.0.2


### Detection

Examine cloud provider logs for unexpected token exchanges, as well as unexpected access to cloud vault secrets.

If you find evidence that this vulnerability has been exploited, please contact [security@kubernetes.io](https://groups.google.com/)

### Acknowledgements

This vulnerability was reported by Reem Rotenberg and [Kas Dekel](https://github.com/privmickas) from Microsoft.

## References
- https://github.com/kubernetes-sigs/secrets-store-sync-controller/security/advisories/GHSA-rcw7-pqfp-735x
- https://nvd.nist.gov/vuln/detail/CVE-2025-7445
- https://github.com/kubernetes/kubernetes/issues/133897
- https://github.com/kubernetes-sigs/secrets-store-sync-controller
- https://groups.google.com/g/kubernetes-security-announce/c/NP7cQvQ1aGA
