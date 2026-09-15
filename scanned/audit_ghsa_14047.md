# [M] ReactPHP's HTTP server continues parsing unused multipart parts after reaching input field and file upload limits

## Summary
Severity: Medium
Advisory: GHSA-95x4-j7vc-h8mf
CVE: CVE-2023-26044
CWE: CWE-400
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2023-05-17
Source: https://github.com/advisories/GHSA-95x4-j7vc-h8mf
Type: github-advisory

## Affected
- Packagist: `react/http` — affected >=0.8.0 <1.9.0

## Details
### Summary

Previous versions of ReactPHP's HTTP server component contain a potential DoS vulnerability that can cause high CPU load when processing large HTTP request bodies. This vulnerability has little to no impact on the default configuration, but can be exploited when explicitly using the  `RequestBodyBufferMiddleware` with very large settings. This might lead to consuming large amounts of CPU time for processing requests and significantly delay or slow down the processing of legitimate user requests.

### Patches

The supplied patch resolves this vulnerability for ReactPHP.

### Workarounds

- Keeping the request body limit using `RequestBodyBufferMiddleware` sensible will mitigate it.

- Infrastructure or DevOps can place a reverse proxy in front of the ReactPHP HTTP server to filter out any excessive HTTP request bodies.

### References

A similar vulnerability was discovered in PHP recently, see also [PHP's security advisory](https://github.com/php/php-src/security/advisories/GHSA-54hq-v5wp-fqgv) (CVE-2023-0662). The fix is based on the [PHP-FPM fix](https://github.com/php/php-src/commit/716de0cff539f46294ef70fe75d548cd66766370#diff-81d659aa9e83177ac08151f99cebf21ab331d22462c72a1039f59947e66f5a35).

## References
- https://github.com/php/php-src/security/advisories/GHSA-54hq-v5wp-fqgv
- https://github.com/reactphp/http/security/advisories/GHSA-95x4-j7vc-h8mf
- https://nvd.nist.gov/vuln/detail/CVE-2023-26044
- https://github.com/php/php-src/commit/716de0cff539f46294ef70fe75d548cd66766370#diff-81d659aa9e83177ac08151f99cebf21ab331d22462c72a1039f59947e66f5a35
- https://github.com/reactphp/http/commit/9681f764b80c45ebfb5fe2ea7da5bd3babfcdcfd
- https://github.com/FriendsOfPHP/security-advisories/blob/master/react/http/CVE-2023-26044.yaml
- https://github.com/advisories/GHSA-95x4-j7vc-h8mf
- https://github.com/reactphp/http
- https://github.com/reactphp/http/releases/tag/v1.9.0
