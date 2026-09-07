# [H] /user/sessions endpoint allows detecting valid accounts

## Summary
Severity: High
Advisory: GHSA-7vwg-39h8-8qp8
CWE: CWE-203
Ecosystem: Packagist
Published: 2021-03-11
Source: https://github.com/advisories/GHSA-7vwg-39h8-8qp8
Type: github-advisory

## Affected
- Packagist: `ezsystems/ezplatform-rest` — affected >=1.2.0 <1.2.2.1
- Packagist: `ezsystems/ezplatform-rest` — affected >=1.3.0 <1.3.1.1

## Details
This Security Advisory is about a vulnerability in eZ Platform v1.13, v2.5, and v3.2, and in Ibexa DXP and Ibexa Open Source v3.3. The /user/sessions endpoint can let an attacker detect if a given username or email refers to a valid account. This can be detected through differences in the response data or response time of certain requests. The fix ensures neither attack is possible. The fix is distributed via Composer.

If you come across a security issue in our products, here is how you can report it to us: https://doc.ibexa.co/en/latest/guide/reporting_issues/#toc

## References
- https://github.com/ezsystems/ezplatform-rest/security/advisories/GHSA-7vwg-39h8-8qp8
- https://github.com/ezsystems/ezplatform-rest/commit/e239bba8b154a3b4cf787e29b9f15edf8945d933
- https://packagist.org/packages/ezsystems/ezplatform-rest
