# [M] copyparty Reflected XSS via Filter Parameter

## Summary
Severity: Medium
Advisory: GHSA-8mx2-rjh8-q3jq
CVE: CVE-2025-54589
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-07-31
Source: https://github.com/advisories/GHSA-8mx2-rjh8-q3jq
Type: github-advisory

## Affected
- PyPI: `copyparty` — affected >=0 <1.18.7

## Details
### Summary
Unauthorized reflected Cross-Site-Scripting when accessing the URL for recent uploads with the `filter` parameter containing JavaScript code.

### Details
When accessing the recent uploads page at `/?ru`, users can filter the results using an input field at the top. This field appends a filter parameter to the URL, which reflects its value directly into a `<script>` block without proper escaping.
This vulnerability allows for reflected Cross-Site Scripting (XSS) and can be exploited against both authenticated and unauthenticated users, enabling unwanted actions in the victims browser.

### PoC
A URL like this will execute `alert(1)`:
```
https://127.0.0.1:3923/?ru&filter=</script><script>alert(1)</script>
```

## References
- https://github.com/9001/copyparty/security/advisories/GHSA-8mx2-rjh8-q3jq
- https://nvd.nist.gov/vuln/detail/CVE-2025-54589
- https://github.com/9001/copyparty/commit/a8705e611d05eeb22be5d3d7d9ab5c020fe54c62
- https://github.com/9001/copyparty
- https://github.com/9001/copyparty/releases/tag/v1.18.7
