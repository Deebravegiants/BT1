# [H] Intermittent HTTP policy bypass

## Summary
Severity: High
Advisory: GHSA-68mj-9pjq-mc85
CVE: CVE-2024-28248
CWE: CWE-693
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-03-18
Source: https://github.com/advisories/GHSA-68mj-9pjq-mc85
Type: github-advisory

## Affected
- Go: `github.com/cilium/cilium` — affected >=1.13.9 <1.13.13
- Go: `github.com/cilium/cilium` — affected >=1.14.0 <1.14.8
- Go: `github.com/cilium/cilium` — affected >=1.15.0 <1.15.2

## Details
### Impact

Cilium's [HTTP policies](https://docs.cilium.io/en/stable/security/policy/language/#http) are not consistently applied to all traffic in the scope of the policies, leading to HTTP traffic being incorrectly and intermittently forwarded when it should be dropped.

### Patches

This issue affects:

* Cilium v1.13 between v1.13.9 and v1.13.12 inclusive
* Cilium v1.14 between v1.14.0 and v1.14.7 inclusive
* Cilium v1.15.0 and v1.15.1

This issue has been patched in:

* Cilium v1.15.2
* Cilium v1.14.8
* Cilium v1.13.13

### Workarounds

There is no workaround for this issue – affected users are strongly encouraged to upgrade.

### Acknowledgements

The Cilium community has worked together with members of Isovalent to prepare these mitigations. Special thanks to @romikps for discovering and reporting this issue, and @sayboras and @jrajahalme for preparing the fix.

### For more information

If you have any questions or comments about this advisory, please reach out on [Slack](https://docs.cilium.io/en/latest/community/community/#slack).

If you think you have found a vulnerability affecting Cilium, we strongly encourage you to report it to our security mailing list at [security@cilium.io](mailto:security@cilium.io). This is a private mailing list for the Cilium internal security team, and your report will be treated as top priority.

## References
- https://github.com/cilium/cilium/security/advisories/GHSA-68mj-9pjq-mc85
- https://nvd.nist.gov/vuln/detail/CVE-2024-28248
- https://docs.cilium.io/en/stable/security/policy/language/#http
- https://github.com/cilium/cilium
- https://github.com/cilium/cilium/releases/tag/v1.13.13
- https://github.com/cilium/cilium/releases/tag/v1.14.8
- https://github.com/cilium/cilium/releases/tag/v1.15.2
