# [M] Hono: Non-breaking space prefix bypass in cookie name handling in getCookie()

## Summary
Severity: Medium
Advisory: GHSA-r5rp-j6wh-rvv4
CVE: CVE-2026-39410
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-r5rp-j6wh-rvv4
Type: github-advisory

## Affected
- npm: `hono` — affected >=0 <4.12.12

## Details
## Summary

A discrepancy between browser cookie parsing and `parse()` handling allows cookie prefix protections to be bypassed.

Cookie names that are treated as distinct by the browser may be normalized to the same key by `parse()`, allowing attacker-controlled cookies to override legitimate ones.

## Details

Browsers follow RFC 6265bis and only trim SP (`0x20`) and HTAB (`0x09`) from cookie names. Other characters, such as the non-breaking space (`U+00A0`), are preserved as part of the cookie name.

For example, the browser treats the following cookies as distinct:

```
"dummy-cookie"
"\u00a0dummy-cookie"
```

However, `parse()` previously used JavaScript's `trim()`, which removes a broader set of characters including `U+00A0`. As a result, both names are normalized to:

```
"dummy-cookie"
```

This mismatch allows attacker-controlled cookies with a `U+00A0` prefix to shadow or override legitimate cookies when accessed via `getCookie()`.

## Impact

An attacker who can set cookies (e.g., via a man-in-the-middle on a non-secure page or other injection vector) can bypass cookie prefix protections and override sensitive cookies.

This may lead to:

* Bypassing `__Secure-` and `__Host-` prefix protections
* Overriding cookies that rely on the Secure attribute
* Session fixation or session hijacking depending on application usage

This issue affects applications that rely on `getCookie()` for security-sensitive cookie handling.

## References
- https://github.com/honojs/hono/security/advisories/GHSA-r5rp-j6wh-rvv4
- https://nvd.nist.gov/vuln/detail/CVE-2026-39410
- https://github.com/honojs/hono/commit/cc067c85592415cb1880ad3c61ed923472452ec0
- https://github.com/honojs/hono
- https://github.com/honojs/hono/releases/tag/v4.12.12
