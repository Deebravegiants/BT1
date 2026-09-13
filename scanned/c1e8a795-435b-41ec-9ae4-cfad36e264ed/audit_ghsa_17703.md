# [M] Cilium has an information leakage via insecure default Hubble UI CORS header

## Summary
Severity: Medium
Advisory: GHSA-h78m-j95m-5356
CVE: CVE-2025-23047
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-01-22
Source: https://github.com/advisories/GHSA-h78m-j95m-5356
Type: github-advisory

## Affected
- Go: `github.com/cilium/cilium` — affected >=1.14.0 <1.14.19
- Go: `github.com/cilium/cilium` — affected >=1.15.0 <1.15.13
- Go: `github.com/cilium/cilium` — affected >=1.16.0 <1.16.6

## Details
### Impact

For users who deploy Hubble UI using either Cilium CLI or via the Cilium Helm chart, an insecure default `Access-Control-Allow-Origin` header value could lead to sensitive data exposure. A user with access to a Hubble UI instance affected by this issue could leak configuration details about the Kubernetes cluster which Hubble UI is monitoring, including node names, IP addresses, and other metadata about workloads and the cluster networking configuration. In order for this vulnerability to be exploited, a victim would have to first visit a malicious page.

### Patches

This issue was patched in https://github.com/cilium/cilium/commit/a3489f190ba6e87b5336ee685fb6c80b1270d06d

This issue affects:

- Cilium between v1.14.0 and v1.14.18 inclusive
- Cilium between v1.15.0 and v1.15.12 inclusive
- Cilium between v1.16.0 and v1.16.5 inclusive

This issue is patched in:

- Cilium v1.14.19
- Cilium v1.15.13
- Cilium v1.16.6

### Workarounds

Users who deploy Hubble UI using the Cilium Helm chart directly can remove the CORS headers from the Helm template as shown in the [patch](https://github.com/cilium/cilium/commit/a3489f190ba6e87b5336ee685fb6c80b1270d06d).

### Acknowledgements

The Cilium community has worked together with members of Isovalent to prepare these mitigations. Special thanks to @ciffelia for reporting this issue and to @geakstr for the fix.

### For more information
If you have any questions or comments about this advisory, please reach out on [Slack](https://docs.cilium.io/en/latest/community/community/#slack).

If you think you have found a vulnerability affecting Cilium, we strongly encourage you to report it to our security mailing list at [security@cilium.io](mailto:security@cilium.io). This is a private mailing list for the Cilium security team, and your report will be treated as top priority.

## References
- https://github.com/cilium/cilium/security/advisories/GHSA-h78m-j95m-5356
- https://nvd.nist.gov/vuln/detail/CVE-2025-23047
- https://github.com/cilium/cilium/commit/a3489f190ba6e87b5336ee685fb6c80b1270d06d
- https://github.com/cilium/cilium
