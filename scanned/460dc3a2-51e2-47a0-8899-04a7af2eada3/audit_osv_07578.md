# [M] BIT-symfony-2020-5255

## Summary
Severity: Medium
Advisory: BIT-symfony-2020-5255
Aliases: CVE-2020-5255, GHSA-mcx4-f5f5-4859
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-symfony-2020-5255
Type: osv

## Affected
- Bitnami: `symfony` — affected >=5.0.0 <5.0.7

## Details
In Symfony before versions 4.4.7 and 5.0.7, when a `Response` does not contain a `Content-Type` header, affected versions of Symfony can fallback to the format defined in the `Accept` header of the request, leading to a possible mismatch between the response&#39;s content and `Content-Type` header. When the response is cached, this can prevent the use of the website by other users. This has been patched in versions 4.4.7 and 5.0.7.

## References
- https://github.com/symfony/symfony/commit/dca343442e6a954f96a2609e7b4e9c21ed6d74e6
- https://github.com/symfony/symfony/security/advisories/GHSA-mcx4-f5f5-4859
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/C36JLPHUPKDFAX6D5WYFC4ALO2K7RDUQ/
- https://symfony.com/blog/cve-2020-5255-prevent-cache-poisoning-via-a-response-content-type-header
