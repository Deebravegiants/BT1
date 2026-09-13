# [H] Cilium has insecure IPsec transport encryption

## Summary
Severity: High
Advisory: GHSA-pwqm-x5x6-5586
CVE: CVE-2024-28860
CWE: CWE-326
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2024-03-28
Source: https://github.com/advisories/GHSA-pwqm-x5x6-5586
Type: github-advisory

## Affected
- Go: `github.com/cilium/cilium` — affected >=1.4.0 <1.13.14
- Go: `github.com/cilium/cilium` — affected >=1.14.0 <1.14.9
- Go: `github.com/cilium/cilium` — affected >=1.15.0 <1.15.3

## Details
### Impact

Users of [IPsec transparent encryption](https://docs.cilium.io/en/stable/security/network/encryption-ipsec/) in Cilium may be vulnerable to cryptographic attacks that render the transparent encryption ineffective.

In particular, Cilium is vulnerable to the following attacks by a man-in-the-middle attacker:

- Chosen plaintext attacks
- Key recovery attacks
- Replay attacks

These attacks are possible due to an ESP sequence number collision when multiple nodes are configured with the same key. Fixed versions of Cilium use unique keys for each IPsec tunnel established between nodes, resolving all of the above attacks.

**Important:** After upgrading, users must perform a key rotation using the instructions [here](https://docs.cilium.io/en/latest/security/network/encryption-ipsec/#key-rotation) to ensure that they are no longer vulnerable to this issue. Please note that the key rotation instructions have recently been updated, and users must use the new instructions to properly establish secure IPsec tunnels. To validate that the new instructions have been followed properly, ensure that the IPsec Kubernetes secret contains a "+" sign.

### Patches

All prior versions of Cilium that support IPsec transparent encryption (Cilium 1.4 onwards) are affected by this issue.

Patched versions:

- Cilium 1.15.3
- Cilium 1.14.9
- Cilium 1.13.14

### Workarounds

There is no workaround to this issue. IPsec transparent encryption users are strongly encouraged to upgrade.

### Acknowledgements

The Cilium community has worked together with members of Cure53 and Isovalent to prepare these mitigations. Special thanks to @NikAleksandrov and @pchaigno for their work on remediating the issue. Thanks to Marsh Ray, Senior Software Developer at Microsoft, for input and guidance on the fix.

### For more information
If you have any questions or comments about this advisory, please reach out on [Slack](https://docs.cilium.io/en/latest/community/community/#slack).

As usual, if you think you found a related vulnerability, we strongly encourage you to report security vulnerabilities to our private security mailing list: [security@cilium.io](mailto:security@cilium.io) - first, before disclosing them in any public forums. This is a private mailing list where only members of the Cilium internal security team are subscribed to, and is treated as top priority.

## References
- https://github.com/cilium/cilium/security/advisories/GHSA-pwqm-x5x6-5586
- https://nvd.nist.gov/vuln/detail/CVE-2024-28860
- https://github.com/cilium/cilium/commit/311fbce5280491cddceab178d83b06fa23688c72
- https://github.com/cilium/cilium/commit/a1742b478306fa256cd27df1039dfae0537b4149
- https://github.com/cilium/cilium/commit/a652c123331852cca90c74202f993d4170fd37fa
- https://docs.cilium.io/en/stable/security/network/encryption-ipsec
- https://github.com/cilium/cilium
- https://pkg.go.dev/vuln/GO-2024-2666
