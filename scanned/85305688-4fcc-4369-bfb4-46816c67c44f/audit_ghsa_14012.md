# [M] @mittwald/kubernetes's secret contents leaked via debug logging

## Summary
Severity: Medium
Advisory: GHSA-g35x-j6jj-8g7j
CWE: CWE-532
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-05-02
Source: https://github.com/advisories/GHSA-g35x-j6jj-8g7j
Type: github-advisory

## Affected
- npm: `@mittwald/kubernetes` — affected >=0 <3.5.0

## Details
### Impact

When debug logging is enabled (via `DEBUG` environment variable), the Kubernetes client may log all response bodies into the debug log -- including sensitive data from `Secret` resources.

When running in a Kubernetes cluster, this might expose sensitive information to users who are _not_ authorised to access secrets, but have access to Pod logs (either directly using kubectl, or by Pod logs being shipped elsewhere).

### Patches
Upgrade to 3.5.0 or newer.

### Workarounds
Disable debug logging entirely, or exclude the `kubernetes:client` debug item (for example, using `DEBUG=*,-kubernetes:client`).

### References

- https://cwe.mitre.org/data/definitions/532.html

## References
- https://github.com/mittwald/node-kubernetes/security/advisories/GHSA-g35x-j6jj-8g7j
- https://github.com/mittwald/node-kubernetes/commit/04f6809fd438417c343d541e57f76f0040e069cd
- https://github.com/mittwald/node-kubernetes
- https://github.com/mittwald/node-kubernetes/releases/tag/v3.5.0
