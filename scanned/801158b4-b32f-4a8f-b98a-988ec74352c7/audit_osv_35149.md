# [C] 5ire vulnerable to Remote Code Execution (RCE) via mermaid

## Summary
Severity: Critical
Advisory: CVE-2025-68669
Aliases: GHSA-5hpf-p8fw-j349
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2025-12-23
Source: https://osv.dev/vulnerability/CVE-2025-68669
Type: osv

## Details
5ire is a cross-platform desktop artificial intelligence assistant and model context protocol client. In versions 0.15.2 and prior, an RCE vulnerability exists in useMarkdown.ts, where the markdown-it-mermaid plugin is initialized with securityLevel: 'loose'. This configuration explicitly permits the rendering of HTML tags within Mermaid diagram nodes. This issue has not been patched at time of publication.

## References
- https://github.com/nanbingxyz/5ire/blob/c40d05a2b546094789fc727daa5383bb15034442/src/hooks/useMarkdown.ts#L156
- https://github.com/nanbingxyz/5ire/releases/tag/v0.15.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68669.json
- https://github.com/nanbingxyz/5ire/security/advisories/GHSA-5hpf-p8fw-j349
- https://nvd.nist.gov/vuln/detail/CVE-2025-68669
- https://github.com/nanbingxyz/5ire/commit/1fbe40d0bfbfe215370d45b9af856c286d67d3f2
