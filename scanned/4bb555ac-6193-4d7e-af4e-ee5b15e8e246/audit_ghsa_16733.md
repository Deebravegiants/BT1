# [H] Symfony vulnerable to denial of service via a malicious HTTP Host header

## Summary
Severity: High
Advisory: GHSA-v77v-x634-9m56
CVE: CVE-2014-5244
CWE: CWE-1333
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-05-30
Source: https://github.com/advisories/GHSA-v77v-x634-9m56
Type: github-advisory

## Affected
- Packagist: `symfony/http-foundation` — affected >=2.0.0 <2.3.19
- Packagist: `symfony/http-foundation` — affected >=2.4.0 <2.4.9
- Packagist: `symfony/http-foundation` — affected >=2.5.0 <2.5.4
- Packagist: `symfony/symfony` — affected >=2.0.0 <2.3.19
- Packagist: `symfony/symfony` — affected >=2.4.0 <2.4.9
- Packagist: `symfony/symfony` — affected >=2.5.0 <2.5.4

## Details
All 2.0.X, 2.1.X, 2.2.X, 2.3.X, 2.4.X, and 2.5.X versions of the Symfony HttpFoundation component are affected by this security issue.

This issue has been fixed in Symfony 2.3.19, 2.4.9, and 2.5.4. Note that no fixes are provided for Symfony 2.0, 2.1, and 2.2 as they are not maintained anymore.

Description
When an arbitrarily long hostname is sent by a client, its parsing in `Request::getHost()` can lead to a DoS attack, due to the way we validate the hostname via a regular expression.

Resolution
The regular expression used to parse and validate the hostname from the HTTP request has been modified to avoid too much sensitivity to the submitted value length.

The patch for this issue is available here: https://github.com/symfony/symfony/pull/11828

## References
- https://github.com/symfony/symfony/pull/11828
- https://github.com/symfony/symfony/commit/1ee96a8b1b0987ffe2a62dca7ad268bf9edfa9b8
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/http-foundation/CVE-2014-5244.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2014-5244.yaml
- https://symfony.com/blog/cve-2014-5244-denial-of-service-with-a-malicious-http-host-header
- https://symfony.com/cve-2014-5244
