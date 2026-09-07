# [H] OmniFaces: EL injection via crafted resource name in wildcard CDN mapping

## Summary
Severity: High
Advisory: GHSA-vp6r-9m58-5xv8
CVE: CVE-2026-41883
CWE: CWE-917
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-vp6r-9m58-5xv8
Type: github-advisory

## Affected
- Maven: `org.omnifaces:omnifaces` — affected >=0 <1.14.2
- Maven: `org.omnifaces:omnifaces` — affected >=2.0-RC1 <2.7.32
- Maven: `org.omnifaces:omnifaces` — affected >=3.0-RC1 <3.14.16
- Maven: `org.omnifaces:omnifaces` — affected >=4.0-M1 <4.7.5
- Maven: `org.omnifaces:omnifaces` — affected >=5.0-M1 <5.2.3

## Details
### Impact

Server-side EL injection leading to Remote Code Execution (RCE). Affects applications that use `CDNResourceHandler` with a wildcard CDN mapping (e.g. `libraryName:*=https://cdn.example.com/*`). An attacker can craft a resource request
URL containing an EL expression in the resource name, which is evaluated server-side.

The severity depends on the EL implementation and the objects available in the EL context. In the worst case this leads to Remote Code Execution (RCE). At minimum it allows information disclosure and denial of service.

Applications using `CDNResourceHandler` without wildcard mappings (i.e. only explicit resource-to-URL mappings) are **not** affected.

### Patches

Fixed in versions 5.2.3, 4.7.5, 3.14.16, 2.7.32, and 1.14.2. Users should upgrade to the appropriate version for their branch.

### Workarounds

Replace wildcard CDN mappings with explicit resource-to-URL mappings. For example, replace:
```
libraryName:*=https://cdn.example.com/*
```
with individual entries:
```
libraryName:resource1.js=https://cdn.example.com/resource1.js,
libraryName:resource2.js=https://cdn.example.com/resource2.js
```

## References
- https://github.com/omnifaces/omnifaces/security/advisories/GHSA-vp6r-9m58-5xv8
- https://nvd.nist.gov/vuln/detail/CVE-2026-41883
- https://github.com/omnifaces/omnifaces
