# [M] In Cilium, packets from terminating endpoints may not be encrypted in Wireguard-enabled clusters

## Summary
Severity: Medium
Advisory: GHSA-5vxx-c285-pcq4
CVE: CVE-2025-32793
CWE: CWE-319, CWE-362
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2025-04-21
Source: https://github.com/advisories/GHSA-5vxx-c285-pcq4
Type: github-advisory

## Affected
- Go: `github.com/cilium/cilium` — affected >=1.13.0 <1.15.16
- Go: `github.com/cilium/cilium` — affected >=1.16.0 <1.16.9
- Go: `github.com/cilium/cilium` — affected >=1.17.0 <1.17.3

## Details
### Impact

When using [Wireguard transparent encryption](https://docs.cilium.io/en/stable/security/network/encryption-wireguard/#encryption-wg) in a Cilium cluster, packets that originate from a terminating endpoint can leave the source node without encryption due to a race condition in how traffic is processed by Cilium.

### Patches

This issue has been patched in https://github.com/cilium/cilium/pull/38592.

This issue affects:

- Cilium v1.15 between v1.15.0 and v1.15.15 inclusive
- Cilium v1.16 between v1.16.0 and v1.16.8 inclusive
- Cilium v1.17 between v1.17.0 and v1.17.2 inclusive

This issue is fixed in:

- Cilium v1.15.16
- Cilium v1.16.9
- Cilium v1.17.3

### Workarounds

There is no workaround to this issue.

### Acknowledgements

The Cilium community has worked together with members of Isovalent to prepare these mitigations. Special thanks to @gandro  and @pippolo84 for reporting this issue and to @julianwiedmann for the patch.

### For more information

If you think you have found a vulnerability affecting Cilium, we strongly encourage you to report it to our security mailing list at [security@cilium.io](mailto:security@cilium.io). This is a private mailing list for the Cilium security team, and your report will be treated as top priority.

## References
- https://github.com/cilium/cilium/security/advisories/GHSA-5vxx-c285-pcq4
- https://nvd.nist.gov/vuln/detail/CVE-2025-32793
- https://github.com/cilium/cilium/pull/38592
- https://github.com/cilium/cilium/commit/e8543eef05126e9ba8a845dc74e96f4e30f6dba9
- https://github.com/cilium/cilium
