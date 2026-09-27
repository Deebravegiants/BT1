# [H] Coder's AI Bridge Proxy skips TLS certificate verification in default configuration

## Summary
Severity: High
Advisory: GHSA-84rm-42xw-mx52
CVE: CVE-2026-55436
CWE: CWE-295
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-84rm-42xw-mx52
Type: github-advisory

## Affected
- Go: `github.com/coder/coder/v2` — affected >=2.34.0 <2.34.2
- Go: `github.com/coder/coder/v2` — affected >=2.33.0 <2.33.8
- Go: `github.com/coder/coder/v2` — affected >=2.30.0 <2.32.7

## Details
### Summary

The AI Bridge Proxy (`aibridgeproxyd`) created a goproxy server whose default transport set `InsecureSkipVerify: true` and only assigned a secure transport when an upstream proxy was configured. In the default configuration (no upstream proxy), outbound HTTPS to the Coder access URL accepted any TLS certificate.

> **Note:** Practical exploitation requires an on-path (man-in-the-middle) position between the AI Bridge Proxy and the Coder server. Deployments where they are co-located over loopback are effectively unaffected.

### Impact

An attacker positioned between the proxy and the Coder server, via ARP spoofing, DNS poisoning or control of proxy environment variables, could intercept injected Coder session tokens, user-supplied provider API keys (BYOK) and full request and response bodies including prompts and completions. The default transport also honored `HTTP_PROXY` and `HTTPS_PROXY`, allowing environment-based traffic redirection.

### Patches

The fix applies the secure transport (TLS 1.2 or higher using system root CAs) unconditionally. The AI Bridge Proxy was introduced in v2.30.0. Earlier release lines including the v2.29 ESR line are not affected.

The fix is available in the following releases:

| Release line | Patched version |
|---|---|
| 2.34 | [v2.34.2](https://github.com/coder/coder/releases/tag/v2.34.2) |
| 2.33 | [v2.33.8](https://github.com/coder/coder/releases/tag/v2.33.8) |
| 2.32 | [v2.32.7](https://github.com/coder/coder/releases/tag/v2.32.7) |

### Workarounds

Ensure the Coder access URL uses a trusted certificate and secure the network path between the AI Bridge Proxy and the Coder server (for example, loopback or mTLS).

### Resources

- Fix: #26131

### Credits

Coder would like to thank Anthropic's Security Team (ANT-2026-22455) for independently disclosing this issue!

## References
- https://github.com/coder/coder/security/advisories/GHSA-84rm-42xw-mx52
- https://github.com/coder/coder/pull/26131
- https://github.com/coder/coder
