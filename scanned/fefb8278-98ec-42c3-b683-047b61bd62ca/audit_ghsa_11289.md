# [H] Qwik City has array method pollution in FormData processing allows type confusion and DoS

## Summary
Severity: High
Advisory: GHSA-whhv-gg5v-864r
CVE: CVE-2026-32701
CWE: CWE-843
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-whhv-gg5v-864r
Type: github-advisory

## Affected
- npm: `@builder.io/qwik-city` — affected >=0 <1.19.2

## Details
**Summary**

Qwik City improperly inferred arrays from dotted form field names during `FormData` parsing. By submitting mixed array-index and object-property keys for the same path, an attacker could cause user-controlled properties to be written onto values that application code expected to be arrays.

**Description**

When processing `application/x-www-form-urlencoded` or `multipart/form-data` requests, Qwik City converted dotted field names such as `items.0` and `items.1` into nested structures. If a path was interpreted as an array, additional attacker-controlled keys on the same path, such as `items.toString`, `items.push`, `items.valueOf`, or `items.length`, could alter the resulting server-side value in unexpected ways.

Applications that assumed these parsed values were safe arrays could be affected. Depending on application behavior, this could lead to request handling failures, denial of service through malformed array state or oversized lengths, and type confusion in downstream code.

This issue affects form parsing in Qwik City request handling. It does not require authentication if the vulnerable route is publicly reachable.

**Impact**

An attacker can send crafted form submissions that cause parsed input to differ from the application’s expected shape. Possible outcomes include:
- Triggering runtime errors when application code calls array methods on attacker-influenced values
- Inflating array length or otherwise creating malformed structures that increase server work or memory use
- Causing type confusion in application logic that trusts parsed form data to be a normal array

There is no direct evidence that this issue enables confidentiality or integrity impact by itself; the primary risk is denial of service and application instability.

**Patched Versions**

Patched in 1.19.2.

**Workarounds**

Until patched, avoid trusting parsed form data to be a well-formed array when using dotted field names, and validate or normalize action input before using array methods or relying on array shape.

## References
- https://github.com/QwikDev/qwik/security/advisories/GHSA-whhv-gg5v-864r
- https://nvd.nist.gov/vuln/detail/CVE-2026-32701
- https://github.com/QwikDev/qwik/commit/7b5867c3dd8925df9aa96c4296b1e95a4c2af87d
- https://github.com/QwikDev/qwik
