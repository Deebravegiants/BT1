# [M] Symfony has unsafe methods in the Request class

## Summary
Severity: Medium
Advisory: GHSA-p684-f7fh-jv2j
CVE: CVE-2015-2309
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-05-30
Source: https://github.com/advisories/GHSA-p684-f7fh-jv2j
Type: github-advisory

## Affected
- Packagist: `symfony/http-foundation` — affected >=2.0.0 <2.3.27
- Packagist: `symfony/http-foundation` — affected >=2.4.0 <2.5.11
- Packagist: `symfony/http-foundation` — affected >=2.6.0 <2.6.6
- Packagist: `symfony/symfony` — affected >=2.0.0 <2.3.27
- Packagist: `symfony/symfony` — affected >=2.4.0 <2.5.11
- Packagist: `symfony/symfony` — affected >=2.6.0 <2.6.6

## Details
All 2.0.X, 2.1.X, 2.2.X, 2.3.X, 2.4.X, 2.5.X, and 2.6.X versions of the Symfony HttpFoundation component are affected by this security issue.

This issue has been fixed in Symfony 2.3.27, 2.5.11, and 2.6.6. Note that no fixes are provided for Symfony 2.0, 2.1, 2.2, and 2.4 as they are not maintained anymore.

### Description
The Symfony\Component\HttpFoundation\Request class provides a mechanism that ensures it does not trust HTTP header values coming from a "non-trusted" client. Unfortunately, it assumes that the remote address is always a trusted client if at least one trusted proxy is involved in the request; this allows a man-in-the-middle attack between the latest trusted proxy and the web server.

The following methods are impacted: getPort(), isSecure(), and getHost(), and getClientIps().

### Resolution
All impacted methods now check that the remote address is trusted, which fixes the issue.

The patch for this issue is available [here](https://github.com/symfony/symfony/pull/14166).

## References
- https://github.com/symfony/symfony/pull/14166
- https://github.com/symfony/symfony/commit/6c73f0ce9302a0091bbfbb96f317e400ce16ef84
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/http-foundation/CVE-2015-2309.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2015-2309.yaml
- https://symfony.com/cve-2015-2309
