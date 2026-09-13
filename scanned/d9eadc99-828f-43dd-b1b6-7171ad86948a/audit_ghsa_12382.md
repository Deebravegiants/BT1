# [M] Potential URI resolution path traversal in the AWS SDK for PHP

## Summary
Severity: Medium
Advisory: GHSA-557v-xcg6-rm5m
CVE: CVE-2023-51651
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-12-21
Source: https://github.com/advisories/GHSA-557v-xcg6-rm5m
Type: github-advisory

## Affected
- Packagist: `aws/aws-sdk-php` — affected >=0 <3.288.1

## Details
### Impact
Within the scope of requests to S3 object keys and/or prefixes containing a Unix double-dot, a URI path traversal is possible. The issue exists in the`buildEndpoint` method in the `RestSerializer` component of the AWS SDK for PHP v3 prior to 3.288.1. The `buildEndpoint` method relies on the Guzzle Psr7 `UriResolver` utility, which strips dot segments from the request path in accordance with RFC 3986. Under certain conditions, this could lead to an arbitrary object being accessed.

Versions of the AWS SDK for PHP v3 before 3.288.1 are affected by this issue.

### Patches
Upgrade to the AWS SDK for PHP >= 3.288.1, if you are on version < 3.288.1.

### References
RFC 3986 - [https://datatracker.ietf.org/doc/html/rfc3986](https://datatracker.ietf.org/doc/html/rfc3986#section-5.2.4)

### For more information
If you have any questions or comments about this advisory, please contact [AWS's Security team](mailto:aws-security@amazon.com).

## References
- https://github.com/aws/aws-sdk-php/security/advisories/GHSA-557v-xcg6-rm5m
- https://nvd.nist.gov/vuln/detail/CVE-2023-51651
- https://github.com/aws/aws-sdk-php/commit/aebc9f801438746ac4ade327551576cb75f635f2
- https://github.com/FriendsOfPHP/security-advisories/blob/master/aws/aws-sdk-php/CVE-2023-51651.yaml
- https://github.com/aws/aws-sdk-php
- https://github.com/aws/aws-sdk-php/releases/tag/3.288.1
