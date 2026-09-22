# [H] Content object state fetch functions open to SQL injection

## Summary
Severity: High
Advisory: GHSA-jpwx-ffjq-wr4w
CWE: CWE-89
Ecosystem: Packagist
Published: 2021-09-07
Source: https://github.com/advisories/GHSA-jpwx-ffjq-wr4w
Type: github-advisory

## Affected
- Packagist: `ezsystems/ezpublish-legacy` — affected >=2018.06.0 <2019.03.6.1
- Packagist: `ezsystems/ezpublish-legacy` — affected >=0 <2017.12.7.4

## Details
### Impact
This Security Update is about a vulnerability in eZ Publish Legacy. The content object state code could be vulnerable to SQL injection. There is no known exploit, but one might be possible. If you use Legacy in any way, we strongly recommend that you install this update as soon as possible.

### Patches
The fix is distributed via Composer, see "Patched versions".

## References
- https://github.com/ezsystems/ezpublish-legacy/security/advisories/GHSA-jpwx-ffjq-wr4w
- https://github.com/ezsystems/ezpublish-legacy/commit/f8e3a97afd92efb9148134a4bacb35a875777a42
- https://developers.ibexa.co/security-advisories/ibexa-sa-2021-005-content-object-state-fetch-functions-open-to-sql-injection
- https://github.com/ezsystems/ezpublish-legacy
