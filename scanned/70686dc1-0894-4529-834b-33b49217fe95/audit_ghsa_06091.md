# [M] Mermaid XY Charts are vulnerable to an infinite loop DoS

## Summary
Severity: Medium
Advisory: GHSA-2v8p-3f2j-5mp7
CVE: CVE-2026-71436
CWE: CWE-1325, CWE-835
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:L/SC:N/SI:N/SA:L (CVSS_V4)
Published: 2026-08-06
Source: https://github.com/advisories/GHSA-2v8p-3f2j-5mp7
Type: github-advisory

## Affected
- npm: `mermaid` — affected >=10.6.0 <10.9.8
- npm: `mermaid` — affected >=11.0.0-alpha.1 <11.16.1

## Details
### Impact

Mermaid XY Charts are vulnerable to an infinite loop DoS attack in the `setXAxisRangeData()`, when configuring an X-Axis with invalid parameters.

As each loop appends an element to an array, this would generally only cause an `RangeError: Invalid array length` to appear after a few seconds, but may cause the page/JavaScript process to crash due to memory exhaustion, depending on the environment.

#### Proof-of-concept

```txt
xychart
  x-axis 1 --> 1
  line [1, 2]
```

### Patches

This has been patched in https://github.com/mermaid-js/mermaid/commit/630aa7e5dd417e1f56bff2a1ce8df2c5ad08d289 and released in [Mermaid v11.16.1](https://github.com/mermaid-js/mermaid/releases/tag/mermaid%4011.16.1).

A backport has been made for the v10 branch in ef60adc837d9d5107af21285f01e83dea309bd0a and was released in [Mermaid v10.9.8](https://github.com/mermaid-js/mermaid/releases/tag/v10.9.8)

### Workarounds

There are no known workarounds. Please update to the latest version or apply the patch.

### References

- https://github.com/mermaid-js/mermaid/commit/630aa7e5dd417e1f56bff2a1ce8df2c5ad08d289
- https://github.com/mermaid-js/mermaid/releases/tag/mermaid%4011.16.1
- https://github.com/mermaid-js/mermaid/commit/ef60adc837d9d5107af21285f01e83dea309bd0a
- https://github.com/mermaid-js/mermaid/releases/tag/v10.9.8

## References
- https://github.com/mermaid-js/mermaid/security/advisories/GHSA-2v8p-3f2j-5mp7
- https://github.com/mermaid-js/mermaid/pull/8022
- https://github.com/mermaid-js/mermaid/commit/630aa7e5dd417e1f56bff2a1ce8df2c5ad08d289
- https://github.com/mermaid-js/mermaid/commit/ef60adc837d9d5107af21285f01e83dea309bd0a
- https://github.com/mermaid-js/mermaid
- https://github.com/mermaid-js/mermaid/releases/tag/mermaid@11.16.1
- https://github.com/mermaid-js/mermaid/releases/tag/v10.9.8
