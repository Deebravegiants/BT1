# [M] Mermaid Architecture diagrams are vulnerable to prototype pollution

## Summary
Severity: Medium
Advisory: GHSA-3rrr-jr9j-h3q3
CVE: CVE-2026-71437
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:L/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-08-06
Source: https://github.com/advisories/GHSA-3rrr-jr9j-h3q3
Type: github-advisory

## Affected
- npm: `mermaid` — affected >=11.5.0 <11.16.1

## Details
Rendering an untrusted `architecture-beta` diagram lets the diagram author write an arbitrary property with the value `horizontal` or `vertical` onto `Object.prototype`. A group id of `__proto__` is accepted as a valid parent.

### Impact

Any code in the same realm that reads a property of that name from an arbitrary object, or enumerates an object with bare `for...in`, observes the injected value (which can only be the string `horizontal` or `vertical`.

This may mean corrupted option/config defaults, bypassed truthiness checks, causing denial of service or logic corruption in the embedding application.

Because the injected value cannot be an object or function, this is not directly exploitable for remote code execution.

### PoC

```
architecture-beta
      group mermaidPrototypePollutionMarker(cloud)[Marker]
      service a(server)[A] in __proto__
      service b(server)[B] in mermaidPrototypePollutionMarker
      a:R -- L:b
```

The vulnerable write was introduced in commit [cb0a4703bdf01d47508bde1c08aa9a980d70bc20](https://github.com/mermaid-js/mermaid/commit/cb0a4703bdf01d47508bde1c08aa9a980d70bc20) and first shipped in `mermaid@11.5.0`. The lines are unchanged in every release since.

### Patches

This has been patched by https://github.com/mermaid-js/mermaid/commit/99af3fc35ef0a9a9c8c6314521344d67523ddccf, released in [Mermaid v11.16.1](https://github.com/mermaid-js/mermaid/releases/tag/mermaid%4011.16.1)

### Workarounds

There are no known workarounds. Please update to a patched version.

### References

_Are there any links users can visit to find out more?_

- https://github.com/mermaid-js/mermaid/commit/99af3fc35ef0a9a9c8c6314521344d67523ddccf
- https://github.com/mermaid-js/mermaid/releases/tag/mermaid%4011.16.1

## References
- https://github.com/mermaid-js/mermaid/security/advisories/GHSA-3rrr-jr9j-h3q3
- https://github.com/mermaid-js/mermaid/pull/8022
- https://github.com/mermaid-js/mermaid/commit/99af3fc35ef0a9a9c8c6314521344d67523ddccf
- https://github.com/mermaid-js/mermaid
- https://github.com/mermaid-js/mermaid/releases/tag/mermaid@11.16.1
