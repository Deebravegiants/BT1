# [M] Mermaid radar diagrams are vulnerable to DoS

## Summary
Severity: Medium
Advisory: GHSA-rhh3-jpg6-66xh
CVE: CVE-2026-71439
CWE: CWE-1322, CWE-606
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:L/SC:N/SI:N/SA:L (CVSS_V4)
Published: 2026-08-06
Source: https://github.com/advisories/GHSA-rhh3-jpg6-66xh
Type: github-advisory

## Affected
- npm: `mermaid` — affected >=11.6.0 <11.16.1

## Details
### Impact

Mermaid radar diagrams allow arbitrary large values for `ticks`, which can cause high CPU usage, freezing the webpage/JavaScript process for long periods of time, until the process is eventually killed due to OOM/running out of memory.

#### Proof-of-concept

```txt
radar-beta
  axis a, b
  curve c {1, 1}
  ticks 1000000000
```

### Patches

_Has the problem been patched? What versions should users upgrade to?_

This problem has been patched by https://github.com/mermaid-js/mermaid/commit/59b22fad2b3bb04f87a476c84a8a2b24679e607e, which was released in [Mermaid v11.16.1](https://github.com/mermaid-js/mermaid/releases/tag/mermaid%4011.16.1)

### Workarounds

_Is there a way for users to fix or remediate the vulnerability without upgrading?_

There are no known workarounds without updating to a patched version of mermaid.

### References

_Are there any links users can visit to find out more?_

- https://github.com/mermaid-js/mermaid/commit/59b22fad2b3bb04f87a476c84a8a2b24679e607e
- https://github.com/mermaid-js/mermaid/releases/tag/mermaid%4011.16.1

## References
- https://github.com/mermaid-js/mermaid/security/advisories/GHSA-rhh3-jpg6-66xh
- https://github.com/mermaid-js/mermaid/pull/8022
- https://github.com/mermaid-js/mermaid/commit/59b22fad2b3bb04f87a476c84a8a2b24679e607e
- https://github.com/mermaid-js/mermaid
- https://github.com/mermaid-js/mermaid/releases/tag/mermaid%4011.16.1
