# [H] Improper Neutralization of Script in Attributes in @dcl/single-sign-on-client

## Summary
Severity: High
Advisory: GHSA-vp4f-wxgw-7x8x
CVE: CVE-2023-41049
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-09-04
Source: https://github.com/advisories/GHSA-vp4f-wxgw-7x8x
Type: github-advisory

## Affected
- npm: `@dcl/single-sign-on-client` — affected >=0 <0.1.0

## Details
### Impact
Improper input validation in the `init` function allows arbitrary javascript to be executed using  the `javascript:` prefix

```ts
    SSO.init('javascript:alert("javascript successfully injected")')
```

### Patches

This vulnerability was patched on version `0.1.0`

### Workarounds

This vulnerability can be prevented if user input correctly sanitized or there is no user input pass to the `init` function

## References
- https://github.com/decentraland/single-sign-on-client/security/advisories/GHSA-vp4f-wxgw-7x8x
- https://nvd.nist.gov/vuln/detail/CVE-2023-41049
- https://github.com/decentraland/single-sign-on-client/pull/2
- https://github.com/decentraland/single-sign-on-client/commit/bd20ea9533d0cda30809d929db85b1b76cef855a
- https://github.com/decentraland/single-sign-on-client
