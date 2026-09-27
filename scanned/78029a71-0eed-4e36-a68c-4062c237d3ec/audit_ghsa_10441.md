# [H] Cillium exposes sensitive information included in the cilium-bugtool debug archive

## Summary
Severity: High
Advisory: GHSA-gj49-89wh-h4gj
CVE: CVE-2026-41520
CWE: CWE-200, CWE-312
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-25
Source: https://github.com/advisories/GHSA-gj49-89wh-h4gj
Type: github-advisory

## Affected
- Go: `github.com/cilium/cilium` — affected >=0 <1.17.15
- Go: `github.com/cilium/cilium` — affected >=1.18.0 <1.18.9
- Go: `github.com/cilium/cilium` — affected >=1.19.0 <1.19.3

## Details
### Impact
The output of `cilium-bugtool` can contain sensitive data when the tool is run against Cilium deployments with WireGuard encryption enabled.

Users of [WireGuard Transparent Encryption](https://docs.cilium.io/en/stable/security/network/encryption-wireguard/) are affected.
The sensitive data is  the WireGuard private key (`cilium_wg0.key`) used for node-to-node encrypted communication

`cilium-bugtool` is a debugging tool that is typically invoked manually and does not run during the normal operation of a Cilium cluster. It is also invoked when gathering sysdumps using the Cilium CLI's `cilium sysdump` command.

### Patches
This issue affects:

- Cilium v1.19 between v1.19.0 and v1.19.2 inclusive
- Cilium v1.18 between v1.18.0 and v1.18.8 inclusive
- All versions of Cilium prior to v1.17.15

This issue has been patched in:

- Cilium v1.19.3
- Cilium v1.18.9
- Cilium v1.17.15


### Workarounds
There is no workaround to this issue.

Users who have previously shared bugtool or sysdump archives from WireGuard-enabled nodes should rotate the WireGuard keys on the affected nodes. This can be done by deleting the key file and restarting the Cilium agent, which will generate a new key pair.

### Acknowledgements

The Cilium community has worked together with members of Isovalent to prepare these mitigations. Cillium extends special thanks to @kodareef5  for reporting the issue and  @tklauser for their work on triaging and remediating this issue.

### For more information

If there are any questions or comments about this advisory, please reach out on [Slack](https://docs.cilium.io/en/latest/community/community/).

Cilium strongly encourages the reporting of suspected vulnerabilities to the security mailing list at [security@cilium.io](mailto:security@cilium.io). This is a private mailing list for the Cilium security team, and the report will be treated as top priority.

## References
- https://github.com/cilium/cilium/security/advisories/GHSA-gj49-89wh-h4gj
- https://nvd.nist.gov/vuln/detail/CVE-2026-41520
- https://github.com/cilium/cilium
- https://github.com/cilium/cilium/releases/tag/v1.17.15
- https://github.com/cilium/cilium/releases/tag/v1.18.9
- https://github.com/cilium/cilium/releases/tag/v1.19.3
- http://docs.cilium.io/en/stable/security/network/encryption-wireguard
