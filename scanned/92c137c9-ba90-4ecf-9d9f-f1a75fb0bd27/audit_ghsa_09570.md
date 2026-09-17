# [M] DOMPurify's ADD_TAGS function form bypasses FORBID_TAGS due to short-circuit evaluation

## Summary
Severity: Medium
Advisory: GHSA-39q2-94rc-95cp
CVE: CVE-2026-65903
CWE: CWE-783
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-39q2-94rc-95cp
Type: github-advisory

## Affected
- npm: `dompurify` — affected >=0 <3.4.0

## Details
## Summary
In `src/purify.ts:1117-1123`, `ADD_TAGS` as a function (via `EXTRA_ELEMENT_HANDLING.tagCheck`) bypasses `FORBID_TAGS` due to short-circuit evaluation.

The condition:
```
!(tagCheck(tagName)) && (!ALLOWED_TAGS[tagName] || FORBID_TAGS[tagName])
```
When `tagCheck(tagName)` returns `true`, the entire condition is `false` and the element is kept — `FORBID_TAGS[tagName]` is never evaluated.

## Inconsistency
This contradicts the attribute-side pattern at line 1214 where `FORBID_ATTR` explicitly wins first:
```
if (FORBID_ATTR[lcName]) { continue; }
```
For tags, FORBID should also take precedence over ADD.

## Impact
Applications using both `ADD_TAGS` as a function and `FORBID_TAGS` simultaneously get unexpected behavior — forbidden tags are allowed through. Config-dependent but a genuine logic inconsistency.

## Suggested Fix
Check `FORBID_TAGS` before `tagCheck`:
```
if (FORBID_TAGS[tagName]) { /* remove */ }
else if (tagCheck(tagName) || ALLOWED_TAGS[tagName]) { /* keep */ }
```

## Affected Version
v3.3.3 (commit 883ac15)

## References
- https://github.com/cure53/DOMPurify/security/advisories/GHSA-39q2-94rc-95cp
- https://github.com/cure53/DOMPurify
