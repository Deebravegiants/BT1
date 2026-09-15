# [M] CiliumLocalRedirectPolicy addressMatcher allows cross-namespace service traffic hijacking and can break service translation

## Summary
Severity: Medium
Advisory: GHSA-q6h5-q3q6-f87x
CVE: CVE-2026-53935
CWE: CWE-601
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:L/PR:H/UI:N/S:C/C:L/I:N/A:H (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-q6h5-q3q6-f87x
Type: github-advisory

## Affected
- Go: `github.com/cilium/cilium` — affected >=1.19.0 <1.19.4
- Go: `github.com/cilium/cilium` — affected >=1.18.2 <1.18.10
- Go: `github.com/cilium/cilium` — affected >=0 <1.17.16

## Details
### Impact

Users with the ability to create CiliumLocalRedirectPolicies can specify arbitrary ClusterIPs via addressMatcher, which enables hijacking traffic to Services in any namespace, bypassing the namespace-scoping guarantees enforced by serviceMatcher.

In addition, deleting such a policy can corrupt Cilium's internal service state, causing service translation to stop working entirely for the affected Service.

### Patches

This issue affects:

- Cilium v1.19.0 to v1.19.3 inclusive  (fixed in PR #45584)
- Cilium v1.18.2 to v1.18.9 inclusive (fixed in PR #45585)
- All versions of Cilium prior to v1.17.16 (fixed in PR #45412)

This issue has been patched in:

- Cilium v1.19.4
- Cilium v1.18.10
- Cilium v1.17.16

### Workarounds

There is no workaround to this issue.

### Acknowledgements

The Cilium community has worked together with members of Isovalent to prepare these mitigations. Special thanks to @ysksuzuki for investigating and fixing the issue.

### For more information
If there are any questions or comments about this advisory, please reach out on [Slack](https://docs.cilium.io/en/latest/community/community/).

To report potential vulnerabilities affecting Cilium, it strongly is encouraged to report them through the security mailing list at [security@cilium.io](mailto:security@cilium.io). This is a private mailing list for the Cilium security team, and reports will be treated as a top priority.

## References
- https://github.com/cilium/cilium/security/advisories/GHSA-q6h5-q3q6-f87x
- https://github.com/cilium/cilium/pull/44512
- https://github.com/cilium/cilium/pull/44584
- https://github.com/cilium/cilium/pull/44585
- https://github.com/cilium/cilium
