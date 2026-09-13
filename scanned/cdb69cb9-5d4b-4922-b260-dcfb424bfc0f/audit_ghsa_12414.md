# [M] Denial of service caused by infinite recursion when parsing SVG images

## Summary
Severity: Medium
Advisory: GHSA-3qx2-6f78-w2j2
CVE: CVE-2023-50262
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2023-12-13
Source: https://github.com/advisories/GHSA-3qx2-6f78-w2j2
Type: github-advisory

## Affected
- Packagist: `dompdf/dompdf` — affected >=0 <2.0.4

## Details
### Summary
When parsing SVG images Dompdf performs an initial validation to ensure that paths within the SVG are allowed. One of the validations is that the [SVG document does not reference itself](https://github.com/dompdf/dompdf/blob/v2.0.3/src/Image/Cache.php#L136-L153). However, a recursive chained using two or more SVG documents is not correctly validated. Depending on the system configuration and attack pattern this could exhaust the memory available to the executing process and/or to the server itself.

### Details
php-svg-lib, when run in isolation, does not support SVG references for `image` elements. An SVG document can, however, be referenced and Dompdf will run that reference through the same validation. Dompdf currently includes validation to prevent self-referential `image` references, but a chained reference is not checked. A malicious actor may thus trigger infinite recursion in the validation process by chaining references between two or more SVG images.

### PoC

This following sources can be used to bypass validation provided by Dompdf:

recurse.html
```
<img src="one.svg">
```

one.svg
```
<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
  <image href="two.svg" />
</svg>
```

two.svg
```
<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
  <image href="one.svg" />
</svg>
```

### Impact

When Dompdf parses the above payload, it will crash due after exceeding the allowed execution time or memory usage. An attacker sending multiple request to a system can potentially cause resource exhaustion to the point that the system is unable to handle incoming request.

## References
- https://github.com/dompdf/dompdf/security/advisories/GHSA-3qx2-6f78-w2j2
- https://nvd.nist.gov/vuln/detail/CVE-2023-50262
- https://github.com/dompdf/dompdf/commit/41cbac16f3cf56affa49f06e8dae66d0eac2b593
- https://github.com/FriendsOfPHP/security-advisories/blob/master/dompdf/dompdf/CVE-2023-50262.yaml
- https://github.com/dompdf/dompdf
- https://github.com/dompdf/dompdf/blob/v2.0.3/src/Image/Cache.php#L136-L153
