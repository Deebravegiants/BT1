# [C] Cilium vulnerable to sensitive information disclosure and cluster disruption via local Envoy admin socket access

## Summary
Severity: Critical
Advisory: GHSA-3fcv-jvfp-m4q9
CVE: CVE-2026-49445
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:H (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-3fcv-jvfp-m4q9
Type: github-advisory

## Affected
- Go: `github.com/cilium/cilium` — affected >=1.19.0 <1.19.2
- Go: `github.com/cilium/cilium` — affected >=1.18.0 <1.18.8
- Go: `github.com/cilium/cilium` — affected >=0 <1.17.14

## Details
### Impact

When Cilium L7 functionality is enabled on a cluster, the Envoy instance supporting this functionality creates a world-accessible socket on cluster nodes. A local attacker would be able to access Envoy admin endpoints. Depending on deployment configuration, this can expose sensitive information or allow disruptive administrative operations, such as:

- Exposing TLS secrets
- Disrupting traffic in the cluster
- Terminating the Envoy process  

This issue affects both the embedded and standalone Envoy deployment models.

### Patches

This issue affects:

- Cilium v1.19 between v1.19.0 and v1.19.1 inclusive
- Cilium v1.18 between v1.18.0 and v1.18.7 inclusive
- All versions of Cilium prior to v1.17.14

This issue has been patched in https://github.com/cilium/cilium/pull/44512, included in:

- Cilium v1.19.2
- Cilium v1.18.8
- Cilium v1.17.14

### Workarounds

There is no known workaround to this issue.

### Acknowledgements

The Cilium community has worked together with members of Isovalent to prepare these mitigations. Special thanks to [moemen](https://github.com/moemen) for reporting the issue and [0xch4z](https://github.com/0xch4z) for their work on triaging and remediating this issue.

### For more information

If there are any questions or comments about this advisory, please reach out on [Slack (https://docs.cilium.io/en/latest/community/community/).

If anyone thinks they have found a vulnerability affecting Cilium, it is strongly encouraged to report it to the security mailing list at [security@cilium.io](mailto:security@cilium.io). This is a private mailing list for the Cilium security team, and the report will be treated as a top priority.

## References
- https://github.com/cilium/cilium/security/advisories/GHSA-3fcv-jvfp-m4q9
- https://github.com/cilium/cilium/pull/44512
- https://github.com/cilium/cilium
