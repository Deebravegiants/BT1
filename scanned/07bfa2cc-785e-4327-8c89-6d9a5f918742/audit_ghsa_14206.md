# [H] Debug mode leaks confidential data in Cilium

## Summary
Severity: High
Advisory: GHSA-pg5p-wwp8-97g8
CVE: CVE-2023-29002
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2023-04-19
Source: https://github.com/advisories/GHSA-pg5p-wwp8-97g8
Type: github-advisory

## Affected
- Go: `github.com/cilium/cilium` — affected >=1.7.0
- Go: `github.com/cilium/cilium` — affected >=1.11.0 <1.11.16
- Go: `github.com/cilium/cilium` — affected >=1.12.0 <1.12.9
- Go: `github.com/cilium/cilium` — affected >=1.13.0 <1.13.2

## Details
### Impact

When run in debug mode, Cilium may log sensitive information.

In particular, Cilium running in debug mode will log the values of headers if they match HTTP network policy rules. This issue affects Cilium versions:

- 1.7.* to 1.10.* inclusive
- 1.11.* before 1.11.16
- 1.12.* before 1.12.9
- 1.13.* before 1.13.2

In addition, Cilium 1.12.* before 1.12.9 and 1.13.* before 1.13.2., when running in debug mode, might log secrets used by the Cilium agent. This includes TLS private keys for Ingress and GatewayAPI resources, depending on the configuration of the affected cluster. Output of the confidential data would occur at Cilium agent restart, when the secrets are modified, and on creation of Ingress or GatewayAPI resources.

### Patches

This vulnerability is fixed in Cilium releases 1.11.16, 1.12.9, and 1.13.2.

### Workarounds
Disable debug mode.

### Acknowledgements
The Cilium community has worked together with members of Isovalent to prepare these mitigations. Special thanks to @meyskens for investigating and fixing the issue.

### For more information
If you have any questions or comments about this advisory, please reach out on [Slack](https://docs.cilium.io/en/latest/community/community/#slack).

As usual, if you think you found a related vulnerability, we strongly encourage you to report security vulnerabilities to our private security mailing list: [security@cilium.io](mailto:security@cilium.io) - first, before disclosing them in any public forums. This is a private mailing list where only members of the Cilium internal security team are subscribed to, and is treated as top priority.

## References
- https://github.com/cilium/cilium/security/advisories/GHSA-pg5p-wwp8-97g8
- https://nvd.nist.gov/vuln/detail/CVE-2023-29002
- https://github.com/cilium/cilium
